import os
from fastapi import FastAPI, Depends, HTTPException, BackgroundTasks, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List

import models
import schemas
import crud
from database import SessionLocal, engine
from services.parser import extract_text_from_pdf, parse_target_file
from services.email import test_smtp_connection
import worker
import shutil

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Mailing Engine API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # In prod, specify the frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# --- Config Endpoints ---

@app.get("/api/config", response_model=schemas.UserConfigRead)
def read_config(db: Session = Depends(get_db)):
    config = crud.get_user_config(db)
    if not config:
        # Return empty config if none exists
        return schemas.UserConfigRead(id=0, **schemas.UserConfigBase().dict())
    return config

@app.post("/api/config", response_model=schemas.UserConfigRead)
def update_config(config: schemas.UserConfigCreate, db: Session = Depends(get_db)):
    return crud.create_or_update_user_config(db, config)

@app.post("/api/config/test-smtp")
async def test_smtp(config: schemas.UserConfigCreate):
    # If the frontend passes the masked password string, reject it.
    if config.smtp_password_encrypted == "********":
        raise HTTPException(status_code=400, detail="Please enter your actual App Password. (Do not leave it as ********)")
        
    success, err_msg = await test_smtp_connection(
        smtp_host=config.smtp_host,
        smtp_port=config.smtp_port,
        smtp_username=config.smtp_username,
        smtp_password=config.smtp_password_encrypted,
        sender_email=config.sender_email
    )
    if not success:
        raise HTTPException(status_code=400, detail=f"SMTP Error: {err_msg}")
    return {"message": "SMTP Connection Successful"}

# --- API Key Endpoints ---

@app.get("/api/apikeys", response_model=List[schemas.APIKeyRead])
def get_api_keys(db: Session = Depends(get_db)):
    return crud.get_api_keys(db)

@app.post("/api/apikeys", response_model=schemas.APIKeyRead)
def create_api_key(api_key: schemas.APIKeyCreate, db: Session = Depends(get_db)):
    return crud.create_api_key(db, api_key)

@app.delete("/api/apikeys/{key_id}")
def delete_api_key(key_id: int, db: Session = Depends(get_db)):
    success = crud.delete_api_key(db, key_id)
    if not success:
        raise HTTPException(status_code=404, detail="API Key not found")
    return {"message": "API Key deleted"}

@app.put("/api/apikeys/{key_id}/priority")
def update_api_key_priority(key_id: int, priority: int, db: Session = Depends(get_db)):
    key = crud.update_api_key_priority(db, key_id, priority)
    if not key:
        raise HTTPException(status_code=404, detail="API Key not found")
    return key

# --- Campaign Endpoints ---

@app.get("/api/campaigns", response_model=List[schemas.CampaignListRead])
def read_campaigns(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud.get_campaigns(db, skip=skip, limit=limit)

@app.post("/api/campaigns", response_model=schemas.CampaignRead)
def create_campaign(campaign: schemas.CampaignCreate, db: Session = Depends(get_db)):
    return crud.create_campaign(db, campaign)

@app.get("/api/campaigns/{campaign_id}", response_model=schemas.CampaignRead)
def read_campaign(campaign_id: int, db: Session = Depends(get_db)):
    db_campaign = crud.get_campaign(db, campaign_id=campaign_id)
    if db_campaign is None:
        raise HTTPException(status_code=404, detail="Campaign not found")
    return db_campaign

@app.put("/api/campaigns/{campaign_id}", response_model=schemas.CampaignRead)
def update_campaign(campaign_id: int, campaign_update: schemas.CampaignUpdate, db: Session = Depends(get_db)):
    db_campaign = crud.update_campaign(db, campaign_id, campaign_update)
    if db_campaign is None:
        raise HTTPException(status_code=404, detail="Campaign not found")
    return db_campaign

@app.delete("/api/campaigns/{campaign_id}")
def delete_campaign_endpoint(campaign_id: int, db: Session = Depends(get_db)):
    success = crud.delete_campaign(db, campaign_id)
    if not success:
        raise HTTPException(status_code=404, detail="Campaign not found")
    return {"message": "Campaign deleted successfully"}

@app.post("/api/campaigns/{campaign_id}/upload-resume")
async def upload_resume(campaign_id: int, file: UploadFile = File(...), db: Session = Depends(get_db)):
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF resumes are supported.")
        
    campaign = crud.get_campaign(db, campaign_id)
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
        
    data_dir = os.getenv("DATA_DIR", ".")
    upload_dir = os.path.join(data_dir, "uploads")
    os.makedirs(upload_dir, exist_ok=True)
    file_path = os.path.join(upload_dir, f"resume_{campaign_id}.pdf")
    
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
        
    text = extract_text_from_pdf(file_path)
    
    campaign.resume_file_path = file_path
    campaign.resume_text = text
    db.commit()
    
    return {"message": "Resume uploaded successfully", "parsed_length": len(text)}

@app.post("/api/campaigns/{campaign_id}/upload-targets")
async def upload_targets(campaign_id: int, file: UploadFile = File(...), db: Session = Depends(get_db)):
    campaign = crud.get_campaign(db, campaign_id)
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
        
    data_dir = os.getenv("DATA_DIR", ".")
    upload_dir = os.path.join(data_dir, "uploads")
    os.makedirs(upload_dir, exist_ok=True)
    file_path = os.path.join(upload_dir, f"targets_{campaign_id}_{file.filename}")
    
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
        
    try:
        targets_data = parse_target_file(file_path)
        for target_data in targets_data:
            target_create = schemas.TargetCreate(**target_data)
            crud.create_target(db, campaign_id, target_create)
            
        return {"message": f"Successfully parsed {len(targets_data)} targets"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error parsing file: {e}")

# --- Target & Action Endpoints ---

@app.post("/api/targets/{target_id}/process")
async def process_target(target_id: int, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    target = crud.get_target(db, target_id)
    if not target:
        raise HTTPException(status_code=404, detail="Target not found")
        
    background_tasks.add_task(worker.process_target_enrichment_and_generation, target_id)
    return {"message": "Processing started"}

@app.post("/api/campaigns/{campaign_id}/process-all")
async def process_all_targets(campaign_id: int, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    campaign = crud.get_campaign(db, campaign_id)
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
        
    background_tasks.add_task(worker.process_all_enrichment_task, campaign_id)
    crud.update_campaign_status(db, campaign_id, models.CampaignStatus.IN_PROGRESS)
    return {"message": "Started processing targets"}

@app.post("/api/campaigns/{campaign_id}/approve-all")
def approve_all_targets(campaign_id: int, db: Session = Depends(get_db)):
    campaign = crud.get_campaign(db, campaign_id)
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
        
    count = 0
    for target in campaign.targets:
        if target.status == models.TargetStatus.DRAFT_GENERATED:
            target.status = models.TargetStatus.APPROVED
            count += 1
            
    db.commit()
    return {"message": f"Successfully approved {count} drafts."}

@app.post("/api/campaigns/{campaign_id}/send-all")
async def send_all_approved_targets(campaign_id: int, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    campaign = crud.get_campaign(db, campaign_id)
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
        
    approved_targets = [t for t in campaign.targets if t.status == models.TargetStatus.APPROVED]
    if not approved_targets:
        raise HTTPException(status_code=400, detail="No approved targets to send")
        
    background_tasks.add_task(worker.send_all_approved_emails_task, campaign_id)
    return {"message": f"Queued {len(approved_targets)} emails for sending"}

@app.put("/api/targets/{target_id}", response_model=schemas.TargetRead)
def edit_target(target_id: int, target_update: schemas.TargetUpdate, db: Session = Depends(get_db)):
    target = crud.update_target(db, target_id, target_update)
    if not target:
        raise HTTPException(status_code=404, detail="Target not found")
    return target

@app.post("/api/targets/{target_id}/send")
async def send_target_email(target_id: int, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    target = crud.get_target(db, target_id)
    if not target or target.status != models.TargetStatus.APPROVED:
        raise HTTPException(status_code=400, detail="Target must be in APPROVED status to send")
        
    background_tasks.add_task(worker.send_approved_email, target_id)
    return {"message": "Email sending queued"}
