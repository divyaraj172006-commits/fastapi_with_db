import smtplib
from email.mime.text import MIMEText
from dotenv import load_dotenv
load_dotenv()
import os

app_password = os.environ["APP_PASSWORD"]
sender_email = os.environ["SENDER_EMAIL"]

# Email details
def send_email(receiver_email: str, subject: str, content: str) -> str:
    """Send an email to the specified receiver with the given subject and content."""

    # Create email
    msg = MIMEText(content)
    msg["From"] = sender_email
    msg["To"] = receiver_email
    msg["Subject"] = subject

    # Send email
    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(sender_email, app_password)
        server.sendmail(sender_email, receiver_email, msg.as_string())

    return "✅ Email sent successfully!"