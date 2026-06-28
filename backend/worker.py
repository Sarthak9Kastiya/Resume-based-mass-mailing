import asyncio
from sqlalchemy.orm import Session
from database import SessionLocal
import crud
import models
from services.scraper import perform_search, scrape_url
from services.llm import generate_email
from services.email import send_email_async

async def process_target_enrichment_and_generation(target_id: int):
    """
    Background task to enrich a target's profile and generate the email draft.
    """
    db = SessionLocal()
    try:
        target = crud.get_target(db, target_id)
        if not target:
            return
            
        campaign = crud.get_campaign(db, target.campaign_id)
        config = crud.get_user_config(db)
        
        if not config:
            crud.update_target_status(db, target_id, models.TargetStatus.ENRICHMENT_FAILED, "Missing config")
            return

        if not campaign or not campaign.resume_text:
            crud.update_target_status(db, target_id, models.TargetStatus.ENRICHMENT_FAILED, "Campaign has no resume text. Upload a resume first.")
            return

        api_keys = crud.get_api_keys(db)
        if not api_keys:
            crud.update_target_status(db, target_id, models.TargetStatus.ENRICHMENT_FAILED, "No LLM API keys configured")
            return

        url = target.provided_url
        
        # 1. Scraping & Enrichment (best-effort — NOT a hard requirement)
        scraped_text = target.scraped_raw_text
        if not scraped_text:
            if not url:
                # Search for URL
                query = f"{target.name} {target.organization or ''} {target.designation_or_department or ''} professor website"
                api_key = config.search_api_key_encrypted
                try:
                    url = await perform_search(query, api_key, config.search_api_provider)
                except Exception as e:
                    print(f"Search failed for {target.name}: {e}")
                    url = ""
            
            if url:
                try:
                    scraped_text = await scrape_url(url)
                except Exception as e:
                    print(f"Scrape failed for {target.name} ({url}): {e}")
                    scraped_text = ""
                
            if scraped_text:
                # Save scraped data directly on the ORM object
                target.provided_url = url
                target.scraped_raw_text = scraped_text
                db.commit()
        
        # 2. LLM Generation — proceed even WITHOUT scraped text
        #    We always have: name, organization, department from the uploaded database
        crud.update_target_status(db, target_id, models.TargetStatus.READY_FOR_AI)
        
        # Build context from ALL available data
        context_parts = []

        if target.organization:
            context_parts.append(f"Organization: {target.organization}")
        if target.designation_or_department:
            context_parts.append(f"Department/Area: {target.designation_or_department}")
        if target.email:
            context_parts.append(f"Email: {target.email}")
            
        if target.dynamic_data:
            import json
            try:
                dynamic = json.loads(target.dynamic_data)
                context_parts.append("Additional Details:")
                for k, v in dynamic.items():
                    context_parts.append(f"  - {k.capitalize()}: {v}")
            except:
                pass

        if scraped_text:
            context_parts.append(f"\nWeb Research:\n{scraped_text}")
        else:
            context_parts.append("\n(No web data available — generate email based on the above profile info and resume.)")
        
        target_full_text = "\n".join(context_parts)
            
        subject, body = await generate_email(
            resume_text=campaign.resume_text,
            target_text=target_full_text,
            target_name=target.name,
            sender_name=config.sender_name or "Sender",
            api_keys=api_keys,
            attach_resume=campaign.attach_resume,
            ai_context=campaign.context or ""
        )
        
        # Override subject if constant before checking 'if subject and body'
        if campaign.subject_type == "constant" and campaign.constant_subject:
            subject = campaign.constant_subject
        elif not subject:
            subject = "Inquiry regarding Internship" # Fallback
            
        if subject and body:
            # Append signature
            if campaign.signature:
                body += f"\n\n{campaign.signature}"

            target.ai_generated_subject = subject
            target.ai_generated_body = body
            target.status = models.TargetStatus.DRAFT_GENERATED
            target.error_log = None  # Clear any previous error
            db.commit()
        else:
            crud.update_target_status(db, target_id, models.TargetStatus.ENRICHMENT_FAILED, "LLM failed to generate content")
            
    except Exception as e:
        print(f"Error processing target {target_id}: {e}")
        import traceback
        traceback.print_exc()
        try:
            crud.update_target_status(db, target_id, models.TargetStatus.ENRICHMENT_FAILED, str(e)[:500])
        except:
            pass
    finally:
        db.close()

async def send_approved_email(target_id: int):
    """
    Background task to send an approved email.
    """
    db = SessionLocal()
    try:
        target = crud.get_target(db, target_id)
        if not target or target.status != models.TargetStatus.APPROVED:
            return
            
        crud.update_target_status(db, target_id, models.TargetStatus.SENDING)
        
        campaign = crud.get_campaign(db, target.campaign_id)
        config = crud.get_user_config(db)
        
        if not config or not config.smtp_host:
            crud.update_target_status(db, target_id, models.TargetStatus.DELIVERY_FAILED, "Missing SMTP Config")
            return
            
        success = await send_email_async(
            smtp_host=config.smtp_host,
            smtp_port=config.smtp_port,
            smtp_username=config.smtp_username,
            smtp_password=config.smtp_password_encrypted,
            sender_name=config.sender_name,
            sender_email=config.sender_email,
            recipient_email=target.email,
            subject=target.ai_generated_subject,
            body=target.ai_generated_body,
            resume_file_path=campaign.resume_file_path if campaign.attach_resume else None
        )
        
        if success:
            crud.update_target_status(db, target_id, models.TargetStatus.SENT)
        else:
            crud.update_target_status(db, target_id, models.TargetStatus.DELIVERY_FAILED, "SMTP connection or send failed")
            
    except Exception as e:
        print(f"Error sending email for target {target_id}: {e}")
        try:
            crud.update_target_status(db, target_id, models.TargetStatus.DELIVERY_FAILED, str(e))
        except:
            pass
    finally:
        db.close()

async def send_all_approved_emails_task(campaign_id: int):
    """
    Background task to send all approved emails sequentially with a rate limit delay.
    """
    db = SessionLocal()
    try:
        import asyncio
        campaign = crud.get_campaign(db, campaign_id)
        if not campaign:
            return
            
        config = crud.get_user_config(db)
        if not config or not config.smtp_host:
            print("Cannot mass mail: SMTP not configured.")
            return

        targets = [t for t in campaign.targets if t.status == models.TargetStatus.APPROVED]
        print(f"Found {len(targets)} targets to mass mail.")
        
        for target in targets:
            await send_approved_email(target.id)
            # 5 second delay to avoid getting rate limited by email providers
            await asyncio.sleep(5)
            
    except Exception as e:
        print(f"Error in mass mailing task for campaign {campaign_id}: {e}")
    finally:
        db.close()

async def process_all_enrichment_task(campaign_id: int):
    """
    Background task to process all targets for enrichment sequentially to avoid AI rate limits.
    """
    db = SessionLocal()
    try:
        import asyncio
        campaign = crud.get_campaign(db, campaign_id)
        if not campaign:
            return
            
        targets = [t for t in campaign.targets if t.status not in [models.TargetStatus.SENT, models.TargetStatus.SENDING]]
        print(f"Found {len(targets)} targets to enrich.")
        
        for target in targets:
            await process_target_enrichment_and_generation(target.id)
            # 8 second delay to avoid hitting LLM API rate limits (especially Gemini/Groq free tiers)
            await asyncio.sleep(8)
            
    except Exception as e:
        print(f"Error in mass enrichment task for campaign {campaign_id}: {e}")
    finally:
        db.close()

