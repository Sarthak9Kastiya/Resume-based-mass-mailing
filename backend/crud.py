from sqlalchemy.orm import Session
import models
import schemas
from typing import List, Optional

def get_api_keys(db: Session) -> List[models.APIKey]:
    return db.query(models.APIKey).order_by(models.APIKey.priority.asc()).all()

def create_api_key(db: Session, api_key: schemas.APIKeyCreate) -> models.APIKey:
    db_api_key = models.APIKey(**api_key.dict())
    db.add(db_api_key)
    db.commit()
    db.refresh(db_api_key)
    return db_api_key

def delete_api_key(db: Session, key_id: int) -> bool:
    db_key = db.query(models.APIKey).filter(models.APIKey.id == key_id).first()
    if db_key:
        db.delete(db_key)
        db.commit()
        return True
    return False

def update_api_key_priority(db: Session, key_id: int, priority: int) -> Optional[models.APIKey]:
    db_key = db.query(models.APIKey).filter(models.APIKey.id == key_id).first()
    if db_key:
        db_key.priority = priority
        db.commit()
        db.refresh(db_key)
    return db_key

def get_user_config(db: Session) -> Optional[models.UserConfig]:
    return db.query(models.UserConfig).first()

def create_or_update_user_config(db: Session, config: schemas.UserConfigCreate) -> models.UserConfig:
    db_config = db.query(models.UserConfig).first()
    if db_config:
        for var, value in vars(config).items():
            if value is not None:
                setattr(db_config, var, value)
    else:
        db_config = models.UserConfig(**config.dict(exclude_unset=True))
        db.add(db_config)
    db.commit()
    db.refresh(db_config)
    return db_config

def get_campaigns(db: Session, skip: int = 0, limit: int = 100) -> List[models.Campaign]:
    return db.query(models.Campaign).order_by(models.Campaign.created_at.desc()).offset(skip).limit(limit).all()

def get_campaign(db: Session, campaign_id: int) -> Optional[models.Campaign]:
    return db.query(models.Campaign).filter(models.Campaign.id == campaign_id).first()

def create_campaign(db: Session, campaign: schemas.CampaignCreate) -> models.Campaign:
    db_campaign = models.Campaign(name=campaign.name)
    db.add(db_campaign)
    db.commit()
    db.refresh(db_campaign)
    return db_campaign

def update_campaign_status(db: Session, campaign_id: int, status: str):
    db_campaign = db.query(models.Campaign).filter(models.Campaign.id == campaign_id).first()
    if db_campaign:
        db_campaign.status = status
        db.commit()
        db.refresh(db_campaign)
    return db_campaign

def update_campaign(db: Session, campaign_id: int, campaign_update: schemas.CampaignUpdate) -> Optional[models.Campaign]:
    db_campaign = db.query(models.Campaign).filter(models.Campaign.id == campaign_id).first()
    if db_campaign:
        update_data = campaign_update.dict(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_campaign, key, value)
        db.commit()
        db.refresh(db_campaign)
    return db_campaign

def delete_campaign(db: Session, campaign_id: int) -> bool:
    db_campaign = db.query(models.Campaign).filter(models.Campaign.id == campaign_id).first()
    if db_campaign:
        db.delete(db_campaign)
        db.commit()
        return True
    return False

def get_target(db: Session, target_id: int) -> Optional[models.Target]:
    return db.query(models.Target).filter(models.Target.id == target_id).first()

def create_target(db: Session, campaign_id: int, target: schemas.TargetCreate) -> models.Target:
    db_target = models.Target(**target.dict(), campaign_id=campaign_id)
    db.add(db_target)
    db.commit()
    db.refresh(db_target)
    return db_target

def update_target(db: Session, target_id: int, target_update: schemas.TargetUpdate) -> Optional[models.Target]:
    db_target = db.query(models.Target).filter(models.Target.id == target_id).first()
    if db_target:
        update_data = target_update.dict(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_target, key, value)
        db.commit()
        db.refresh(db_target)
    return db_target

def update_target_status(db: Session, target_id: int, status: str, error_log: str = None) -> Optional[models.Target]:
    db_target = db.query(models.Target).filter(models.Target.id == target_id).first()
    if db_target:
        db_target.status = status
        if error_log is not None:
            db_target.error_log = error_log
        db.commit()
        db.refresh(db_target)
    return db_target
