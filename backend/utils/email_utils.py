import os
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig, MessageType
from pydantic import EmailStr
from dotenv import load_dotenv

load_dotenv()

conf = ConnectionConfig(
    MAIL_USERNAME=os.getenv("EMAIL_USER"),
    MAIL_PASSWORD=os.getenv("EMAIL_PASS"),
    MAIL_FROM=os.getenv("EMAIL_USER"),
    MAIL_PORT=465,
    MAIL_SERVER="smtp.gmail.com",
    MAIL_STARTTLS=False,
    MAIL_SSL_TLS=True,
    USE_CREDENTIALS=True,
    VALIDATE_CERTS=True
)

async def send_invitation_email(email: str, username: str, password: str, role: str, ward_id: str = None):
    subject = f"Invitation to AURORA Platform - {role}"
    
    body = f"""
    <html>
        <body style="font-family: sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px; border: 1px solid #e0e0e0; rounded: 8px;">
                <h2 style="color: #2563eb;">Welcome to AURORA</h2>
                <p>You have been invited to join the <strong>AURORA Urban Flood Intelligence Platform</strong> as a <strong>{role}</strong>.</p>
                <div style="background: #f3f4f6; padding: 15px; border-radius: 8px; margin: 20px 0;">
                    <p style="margin: 0;"><strong>Username:</strong> {username}</p>
                    <p style="margin: 5px 0 0 0;"><strong>Password:</strong> {password}</p>
                    {f'<p style="margin: 5px 0 0 0;"><strong>Assigned Ward:</strong> {ward_id}</p>' if ward_id else ''}
                </div>
                <p>Please log in to the dashboard and change your password immediately.</p>
                <p style="font-size: 12px; color: #666; margin-top: 30px; border-top: 1px solid #eee; padding-top: 10px;">
                    This is an automated message from the AURORA Governance System.
                </p>
            </div>
        </body>
    </html>
    """

    message = MessageSchema(
        subject=subject,
        recipients=[email],
        body=body,
        subtype=MessageType.html
    )

    fm = FastMail(conf)
    await fm.send_message(message)
