import aiosmtplib
from email.message import EmailMessage

async def send_email_async(
    smtp_host: str,
    smtp_port: int,
    smtp_username: str,
    smtp_password: str,
    sender_name: str,
    sender_email: str,
    recipient_email: str,
    subject: str,
    body: str,
    resume_file_path: str = None
) -> bool:
    """
    Sends an email asynchronously using aiosmtplib.
    Optionally attaches the resume.
    """
    try:
        message = EmailMessage()
        message["From"] = f"{sender_name} <{sender_email}>"
        message["To"] = recipient_email
        message["Subject"] = subject
        message.set_content(body)

        if resume_file_path:
            try:
                import mimetypes
                import os
                
                ctype, encoding = mimetypes.guess_type(resume_file_path)
                if ctype is None or encoding is not None:
                    ctype = "application/octet-stream"
                maintype, subtype = ctype.split("/", 1)
                
                with open(resume_file_path, "rb") as f:
                    message.add_attachment(
                        f.read(),
                        maintype=maintype,
                        subtype=subtype,
                        filename=os.path.basename(resume_file_path)
                    )
            except Exception as e:
                print(f"Failed to attach resume: {e}")

        # Connect and send. Force IPv4 to prevent Railway IPv6 timeouts.
        import socket
        sock = None
        try:
            addr_info = socket.getaddrinfo(smtp_host, smtp_port, socket.AF_INET)
            ipv4_ip = addr_info[0][4][0]
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(5.0)  # Prevent hanging indefinitely
            sock.connect((ipv4_ip, smtp_port))
            sock.settimeout(None) # Reset for aiosmtplib
        except Exception as e:
            print(f"Failed to create IPv4 socket, falling back to default: {e}")
            sock = None

        if sock:
            await aiosmtplib.send(
                message,
                hostname=smtp_host,
                sock=sock,
                username=smtp_username,
                password=smtp_password,
                start_tls=True if smtp_port == 587 else False,
                use_tls=True if smtp_port == 465 else False
            )
        else:
            await aiosmtplib.send(
                message,
                hostname=smtp_host,
                port=smtp_port,
                username=smtp_username,
                password=smtp_password,
                start_tls=True if smtp_port == 587 else False,
                use_tls=True if smtp_port == 465 else False
            )
        return True
    except Exception as e:
        print(f"Error sending email to {recipient_email}: {e}")
        return False

async def test_smtp_connection(
    smtp_host: str,
    smtp_port: int,
    smtp_username: str,
    smtp_password: str,
    sender_email: str
) -> tuple[bool, str]:
    """
    Tests SMTP connection by sending a simple test email to oneself.
    Returns (success, error_message).
    """
    try:
        message = EmailMessage()
        message["From"] = f"Mailing Engine <{sender_email}>"
        message["To"] = sender_email
        message["Subject"] = "Test Connection - Mailing Engine"
        message.set_content("If you are receiving this, your SMTP configuration is correct.")

        # Connect and send. Force IPv4 to prevent Railway IPv6 timeouts.
        import socket
        sock = None
        try:
            addr_info = socket.getaddrinfo(smtp_host, smtp_port, socket.AF_INET)
            ipv4_ip = addr_info[0][4][0]
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(5.0)  # Prevent hanging indefinitely
            sock.connect((ipv4_ip, smtp_port))
            sock.settimeout(None) # Reset for aiosmtplib
        except Exception as e:
            print(f"Failed to create IPv4 socket in test, falling back: {e}")
            sock = None

        if sock:
            await aiosmtplib.send(
                message,
                hostname=smtp_host,
                sock=sock,
                username=smtp_username,
                password=smtp_password,
                start_tls=True if smtp_port == 587 else False,
                use_tls=True if smtp_port == 465 else False,
                timeout=10.0
            )
        else:
            await aiosmtplib.send(
                message,
                hostname=smtp_host,
                port=smtp_port,
                username=smtp_username,
                password=smtp_password,
                start_tls=True if smtp_port == 587 else False,
                use_tls=True if smtp_port == 465 else False,
                timeout=10.0
            )
        return True, "Success"
    except Exception as e:
        print(f"SMTP Test Error: {e}")
        return False, str(e)
