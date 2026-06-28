import sqlite3

def upgrade_db():
    conn = sqlite3.connect('mailing_engine.db')
    cursor = conn.cursor()

    # Create api_keys table
    try:
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS api_keys (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name VARCHAR,
            provider VARCHAR,
            model_name VARCHAR,
            key_encrypted VARCHAR,
            priority INTEGER DEFAULT 0
        )
        ''')
        cursor.execute("CREATE INDEX IF NOT EXISTS ix_api_keys_name ON api_keys(name)")
        print("Created api_keys table")
    except Exception as e:
        print(f"Error creating api_keys: {e}")

    # Alter campaigns table
    try:
        cursor.execute("ALTER TABLE campaigns ADD COLUMN subject_type VARCHAR DEFAULT 'personalized'")
    except Exception as e:
        print(f"campaigns.subject_type: {e}")
        
    try:
        cursor.execute("ALTER TABLE campaigns ADD COLUMN constant_subject VARCHAR")
    except Exception as e:
        print(f"campaigns.constant_subject: {e}")
        
    try:
        cursor.execute("ALTER TABLE campaigns ADD COLUMN signature TEXT")
    except Exception as e:
        print(f"campaigns.signature: {e}")
        
    try:
        cursor.execute("ALTER TABLE campaigns ADD COLUMN context TEXT")
    except Exception as e:
        print(f"campaigns.context: {e}")
        
    try:
        cursor.execute("ALTER TABLE campaigns ADD COLUMN attach_resume BOOLEAN DEFAULT 0")
    except Exception as e:
        print(f"campaigns.attach_resume: {e}")

    # Alter targets table
    try:
        cursor.execute("ALTER TABLE targets ADD COLUMN dynamic_data TEXT")
    except Exception as e:
        print(f"targets.dynamic_data: {e}")
        
    # We can't DROP COLUMN easily in SQLite, so we'll just leave the old columns 
    # (llm_provider, gemini_api_key_encrypted, etc.) in user_configs. 
    # SQLAlchemy will just ignore them since we removed them from the model.

    conn.commit()
    conn.close()
    print("Database upgrade complete.")

if __name__ == '__main__':
    upgrade_db()
