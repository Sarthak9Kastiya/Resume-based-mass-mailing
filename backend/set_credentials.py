import getpass
from database import SessionLocal
import models

def main():
    print("=== SMTP Configuration ===")
    print("This script will save your email credentials to the database.")
    print("Your credentials will be stored in your local database for the automated mass mailing system.\n")
    
    smtp_host = input("SMTP Host (e.g., smtp.gmail.com): ").strip()
    if not smtp_host:
        smtp_host = "smtp.gmail.com"
        
    smtp_port_str = input("SMTP Port (e.g., 587 or 465) [default 587]: ").strip()
    smtp_port = int(smtp_port_str) if smtp_port_str.isdigit() else 587
    
    sender_name = input("Sender Name (e.g., John Doe): ").strip()
    sender_email = input("Email Address: ").strip()
    
    print("\nIf you are using Gmail, you MUST use a 16-character App Password (not your regular password).")
    smtp_password = getpass.getpass("Password / App Password: ").strip()
    
    db = SessionLocal()
    try:
        config = db.query(models.UserConfig).first()
        if not config:
            config = models.UserConfig()
            db.add(config)
            
        config.smtp_host = smtp_host
        config.smtp_port = smtp_port
        config.smtp_username = sender_email
        config.smtp_password_encrypted = smtp_password
        config.sender_name = sender_name
        config.sender_email = sender_email
        
        db.commit()
        print("\n✅ Credentials saved successfully!")
    except Exception as e:
        print(f"\n❌ Error saving credentials: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    main()
