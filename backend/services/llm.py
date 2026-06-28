import openai
from typing import Tuple
from groq import AsyncGroq
from google import genai
import anthropic
import asyncio

def get_default_model(provider: str) -> str:
    p = provider.lower()
    if p == "anthropic": return "claude-opus-4-8"
    if p == "gemini": return "gemini-3.1-pro"
    if p == "openai": return "gpt-5.5"
    if p == "deepseek": return "deepseek-v4-pro"
    if p == "mistral": return "mistral-large-3"
    if p == "perplexity": return "sonar-pro"
    if p == "together": return "llama-4-maverick"
    if p == "openrouter": return "anthropic/claude-opus-4-8"
    if p == "groq": return "llama-4-scout"
    return "gpt-5.5"

async def _call_anthropic(system_prompt: str, user_prompt: str, api_key: str, model_name: str) -> str:
    client = anthropic.AsyncAnthropic(api_key=api_key)
    response = await client.messages.create(
        model=model_name or get_default_model("anthropic"),
        max_tokens=1024,
        system=system_prompt,
        messages=[
            {"role": "user", "content": user_prompt}
        ]
    )
    return response.content[0].text

async def _call_gemini(system_prompt: str, user_prompt: str, api_key: str, model_name: str) -> str:
    client = genai.Client(api_key=api_key)
    prompt = f"{system_prompt}\n\n{user_prompt}"
    
    def run_sync():
        response = client.models.generate_content(
            model=model_name or get_default_model("gemini"),
            contents=prompt,
        )
        return response.text
        
    return await asyncio.to_thread(run_sync)

async def _call_groq(system_prompt: str, user_prompt: str, api_key: str, model_name: str) -> str:
    client = AsyncGroq(api_key=api_key, timeout=15.0)
    response = await client.chat.completions.create(
        model=model_name or get_default_model("groq"),
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        temperature=0.7,
        max_tokens=1024
    )
    return response.choices[0].message.content.strip()

async def _call_openai_compatible(system_prompt: str, user_prompt: str, api_key: str, model_name: str, base_url: str = None) -> str:
    client_args = {"api_key": api_key, "timeout": 15.0}
    if base_url:
        client_args["base_url"] = base_url
        
    client = openai.AsyncOpenAI(**client_args)
    response = await client.chat.completions.create(
        model=model_name,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        temperature=0.7,
        max_tokens=1024
    )
    return response.choices[0].message.content.strip()

async def generate_email(
    resume_text: str,
    target_text: str,
    target_name: str,
    sender_name: str,
    api_keys: list,
    attach_resume: bool,
    ai_context: str = ""
) -> Tuple[str, str]:
    """
    Generates a personalized email using an LLM.
    Iterates through api_keys list in order.
    Returns (subject, body).
    """
    attach_text = '- MUST end with: "I have attached my resume for your reference."' if attach_resume else ''
    
    user_instructions_block = f"""
    6. CRITICAL OVERRIDE - USER INSTRUCTIONS:
       The user has provided the following additional context and instructions. These instructions OVERRIDE any conflicting rules above. You MUST prioritize these instructions above all else:
       "{ai_context}"
    """ if ai_context else ""

    system_prompt = f"""You are a professional email writer. Write a formal, crisp, and professional cold email for an undergraduate student seeking an internship with a professor.

    STRICT RULES:
    1. TONE: Formal, professional, respectful. NOT desperate, NOT overly casual.
    2. HYPER-PERSONALIZATION LOGIC:
       - You MUST carefully read the professor's details (Designation, Department, Area of Interest, and any extra dynamic details provided).
       - You MUST deeply analyze the student's RESUME to find the specific project, skill, or coursework that best aligns with the professor's department, designation, or extra details.
       - explicitly connect them. E.g. "Given your work in [Area], my experience in [Specific Resume Project] would allow me to contribute meaningfully to your research..."
       - Do NOT fabricate professor details, use only what is provided in the PROFESSOR INFO section.
    3. STRUCTURE:
       - Start with "Respected [Professor Name]," (use "Prof." or "Dr." prefix)
       - Body: 2-3 short paragraphs. Crisp and detailed but SHORT. The core of the email MUST be the hyper-personalized connection.
       {attach_text}
       - MUST end CTA with something like: "Would you be available to connect with me?" or "Would you consider my application for an internship under your guidance?" Do NOT suggest a specific day or time.
       - Do NOT include any signature at the end (no "Warm Regards" etc., this will be added automatically).

    4. OUTPUT FORMAT: Two sections separated by exactly "---BODY---":
       [Subject Line]
       ---BODY---
       [Email Body without signature]
    5. Keep the email body under 200 words unless overridden by user instructions.
    {user_instructions_block}
    """

    user_prompt = f"""
    STUDENT INFO (Sender: {sender_name}):
    {resume_text[:3000]}
    
    PROFESSOR INFO (Recipient: {target_name}):
    {target_text[:3000]}

    Write the email now. It is CRITICAL that you hyper-personalize this email using the professor's details, strictly follow all guidelines in the CRITICAL OVERRIDE instructions (if provided), and use the dynamic data.
    """

    content = None
    errors = []

    sorted_keys = sorted(api_keys, key=lambda k: k.priority)

    for api_key in sorted_keys:
        provider = api_key.provider.lower()
        key_value = api_key.key_encrypted
        model_name = api_key.model_name or get_default_model(provider)
        
        print(f"[LLM] Trying {provider} ({model_name}) for {target_name}...")
        try:
            if provider == "anthropic":
                content = await _call_anthropic(system_prompt, user_prompt, key_value, model_name)
            elif provider == "gemini":
                content = await _call_gemini(system_prompt, user_prompt, key_value, model_name)
            elif provider == "groq":
                content = await _call_groq(system_prompt, user_prompt, key_value, model_name)
            elif provider == "openai":
                content = await _call_openai_compatible(system_prompt, user_prompt, key_value, model_name)
            elif provider == "deepseek":
                content = await _call_openai_compatible(system_prompt, user_prompt, key_value, model_name, "https://api.deepseek.com")
            elif provider == "mistral":
                content = await _call_openai_compatible(system_prompt, user_prompt, key_value, model_name, "https://api.mistral.ai/v1")
            elif provider == "perplexity":
                content = await _call_openai_compatible(system_prompt, user_prompt, key_value, model_name, "https://api.perplexity.ai")
            elif provider == "together":
                content = await _call_openai_compatible(system_prompt, user_prompt, key_value, model_name, "https://api.together.xyz/v1")
            elif provider == "openrouter":
                content = await _call_openai_compatible(system_prompt, user_prompt, key_value, model_name, "https://openrouter.ai/api/v1")
            else:
                raise ValueError(f"Unknown provider: {provider}")
                
            print(f"[LLM] {provider} succeeded for {target_name}")
            break # Success, stop iterating
        except Exception as e:
            print(f"[LLM] {provider} failed for {target_name}: {e}")
            errors.append(f"{provider}: {str(e)[:200]}")

    if not content:
        print(f"[LLM] ALL providers failed for {target_name}. Errors: {errors}")
        return "", ""
        
    try:
        if "---BODY---" in content:
            parts = content.split("---BODY---")
            subject = parts[0].strip().removeprefix("Subject:").strip().strip('"').strip("'")
            body = parts[1].strip()
            return subject, body
        else:
            lines = content.strip().split('\n', 1)
            subject = lines[0].replace('Subject:', '').strip().strip('"').strip("'")
            body = lines[1].strip() if len(lines) > 1 else content
            return subject, body
    except Exception as e:
        print(f"[LLM] Error parsing response for {target_name}: {e}")
        return "", ""
