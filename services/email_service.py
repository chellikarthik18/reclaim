import os, smtplib
from email.message import EmailMessage
from dotenv import load_dotenv
load_dotenv()

def send_found_item_email(student_email, student_name, found_item):
    host = os.getenv("SMTP_HOST")
    port = int(os.getenv("SMTP_PORT", "587"))
    username = os.getenv("SMTP_USERNAME")
    password = os.getenv("SMTP_PASSWORD")
    use_tls = os.getenv("SMTP_USE_TLS", "true").lower() == "true"
    sender = os.getenv("MAIL_FROM") or username
    helpline = os.getenv("HELPLINE_NAME", "RECLAIM Student Helpline Centre")

    if not all([host, username, password, sender]):
        raise RuntimeError("SMTP is not configured. Copy .env.example to .env and configure SMTP credentials.")

    msg = EmailMessage()
    msg["Subject"] = "RECLAIM — Your Lost Item Has Been Found"
    msg["From"] = sender
    msg["To"] = student_email
    msg.set_content(f"""Hello {student_name},

The RECLAIM Student Helpline Centre has verified that an item matching your lost-item report has been found.

Item: {found_item.category} {found_item.brand or ''} {found_item.model or ''}
Found Location: {found_item.location}
Found Date: {found_item.date}

Please contact/visit the Student Helpline Centre to complete the collection process.

Please do not reply with sensitive information.

Regards,
{helpline}
""")

    with smtplib.SMTP(host, port, timeout=20) as smtp:
        if use_tls:
            smtp.starttls()
        smtp.login(username, password)
        smtp.send_message(msg)
