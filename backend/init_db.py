from database import SessionLocal, engine
import models

models.Base.metadata.create_all(bind=engine)
db = SessionLocal()
config = models.UserConfig(
    llm_provider="auto",
    gemini_api_key_encrypted="AQ.Ab8RN6Ks3gSVJ0kclS-O1CfQYMdKz7dqIoOGL8P-72Jedx-ACQ",
    openrouter_api_key_encrypted="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",
    groq_api_key_encrypted="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",
    search_api_provider="tavily"
)
db.add(config)
db.commit()
db.close()
print("Initialized DB with API keys")
