from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Enum, Boolean
from sqlalchemy.orm import relationship
import enum
import datetime
from database import Base

class CampaignStatus(str, enum.Enum):
    DRAFT = "Draft"
    IN_PROGRESS = "In Progress"
    PAUSED = "Paused"
    COMPLETED = "Completed"

class TargetStatus(str, enum.Enum):
    PENDING_INPUT = "Pending Input"
    ENRICHMENT_FAILED = "Enrichment Failed"
    READY_FOR_AI = "Ready for AI"
    DRAFT_GENERATED = "Draft Generated"
    APPROVED = "Approved"
    SENDING = "Sending"
    SENT = "Sent"
    DELIVERY_FAILED = "Delivery Failed"

class APIKey(Base):
    __tablename__ = "api_keys"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    provider = Column(String)  # 'Anthropic', 'Gemini', 'OpenRouter', 'Groq'
    model_name = Column(String) # e.g. 'claude-opus-4-8'
    key_encrypted = Column(String)
    priority = Column(Integer, default=0) # lower number = higher priority

class UserConfig(Base):
    __tablename__ = "user_configs"

    id = Column(Integer, primary_key=True, index=True)
    smtp_host = Column(String, nullable=True)
    smtp_port = Column(Integer, nullable=True)
    smtp_username = Column(String, nullable=True)
    smtp_password_encrypted = Column(String, nullable=True)
    search_api_provider = Column(String, default="tavily") # 'tavily', 'serper'
    search_api_key_encrypted = Column(String, nullable=True)
    sender_name = Column(String, nullable=True)
    sender_email = Column(String, nullable=True)

class Campaign(Base):
    __tablename__ = "campaigns"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    status = Column(String, default=CampaignStatus.DRAFT)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    resume_file_path = Column(String, nullable=True)
    resume_text = Column(Text, nullable=True)
    
    subject_type = Column(String, default="personalized") # 'constant' or 'personalized'
    constant_subject = Column(String, nullable=True)
    signature = Column(Text, nullable=True)
    context = Column(Text, nullable=True)
    attach_resume = Column(Boolean, default=False)

    targets = relationship("Target", back_populates="campaign", cascade="all, delete-orphan")

class Target(Base):
    __tablename__ = "targets"

    id = Column(Integer, primary_key=True, index=True)
    campaign_id = Column(Integer, ForeignKey("campaigns.id"))
    name = Column(String)
    email = Column(String, index=True)
    organization = Column(String, nullable=True)
    designation_or_department = Column(String, nullable=True)
    
    provided_url = Column(String, nullable=True)
    scraped_raw_text = Column(Text, nullable=True)
    dynamic_data = Column(Text, nullable=True) # JSON string of extra CSV columns
    
    ai_generated_subject = Column(String, nullable=True)
    ai_generated_body = Column(Text, nullable=True)
    
    status = Column(String, default=TargetStatus.PENDING_INPUT)
    error_log = Column(Text, nullable=True)

    campaign = relationship("Campaign", back_populates="targets")
