from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from models import CampaignStatus, TargetStatus

class APIKeyBase(BaseModel):
    name: str
    provider: str
    model_name: str
    key_encrypted: str
    priority: Optional[int] = 0

class APIKeyCreate(APIKeyBase):
    pass

class APIKeyRead(APIKeyBase):
    id: int
    class Config:
        orm_mode = True
        from_attributes = True

class UserConfigBase(BaseModel):
    smtp_host: Optional[str] = None
    smtp_port: Optional[int] = None
    smtp_username: Optional[str] = None
    smtp_password_encrypted: Optional[str] = None
    search_api_provider: Optional[str] = "tavily"
    search_api_key_encrypted: Optional[str] = None
    sender_name: Optional[str] = None
    sender_email: Optional[str] = None

class UserConfigCreate(UserConfigBase):
    pass

class UserConfigRead(UserConfigBase):
    id: int
    class Config:
        orm_mode = True
        from_attributes = True

class TargetBase(BaseModel):
    name: str
    email: str
    organization: Optional[str] = None
    designation_or_department: Optional[str] = None
    provided_url: Optional[str] = None
    dynamic_data: Optional[str] = None

class TargetCreate(TargetBase):
    pass

class TargetUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    organization: Optional[str] = None
    designation_or_department: Optional[str] = None
    provided_url: Optional[str] = None
    ai_generated_subject: Optional[str] = None
    ai_generated_body: Optional[str] = None
    status: Optional[str] = None

class TargetRead(TargetBase):
    id: int
    campaign_id: int
    scraped_raw_text: Optional[str] = None
    ai_generated_subject: Optional[str] = None
    ai_generated_body: Optional[str] = None
    status: str
    error_log: Optional[str] = None

    class Config:
        orm_mode = True
        from_attributes = True

class CampaignBase(BaseModel):
    name: str
    subject_type: Optional[str] = "personalized"
    constant_subject: Optional[str] = None
    signature: Optional[str] = None
    context: Optional[str] = None
    attach_resume: Optional[bool] = False

class CampaignUpdate(BaseModel):
    subject_type: Optional[str] = None
    constant_subject: Optional[str] = None
    signature: Optional[str] = None
    context: Optional[str] = None
    attach_resume: Optional[bool] = None

class CampaignCreate(CampaignBase):
    pass

class CampaignRead(CampaignBase):
    id: int
    status: str
    created_at: datetime
    resume_file_path: Optional[str] = None
    resume_text: Optional[str] = None
    targets: List[TargetRead] = []

    class Config:
        orm_mode = True
        from_attributes = True

class CampaignListRead(CampaignBase):
    id: int
    status: str
    created_at: datetime

    class Config:
        orm_mode = True
        from_attributes = True
