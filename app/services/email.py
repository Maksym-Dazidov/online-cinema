import aiosmtplib
from email.message import EmailMessage

from app.core.config import settings


class EmailService:
    def __init__(self):
        self.host = settings.SMTP_HOST
        self.port = settings.SMTP_PORT
        self.username = settings.SMTP_USERNAME
        self.password = settings.SMTP_PASSWORD
        self.from_email = settings.SMTP_FROM

    async def send_email(self, to: str, subject: str, body: str):
        msg = EmailMessage()
        msg["From"] = self.from_email
        msg["To"] = to
        msg["Subject"] = subject
        msg.set_content(body)

        await aiosmtplib.send(
            msg,
            hostname=self.host,
            port=self.port,
            username=self.username,
            password=self.password,
            start_tls=True,
        )

    async def send_activation_email(self, email: str, token: str):
        activation_link = f"{settings.FRONTEND_URL}/auth/activate?token={token}"
        subject = "Activate your account"
        body = (
            f"Hello!\n\n"
            f"Please activate your account using the link below:\n"
            f"{activation_link}\n\n"
            f"This link is valid for 24 hours."
        )
        await self.send_email(email, subject, body)

    async def send_password_reset_email(self, email: str, token: str):
        reset_link = f"{settings.FRONTEND_URL}/auth/reset-password?token={token}"
        subject = "Reset your password"
        body = (
            f"Hello!\n\n"
            f"Use the link below to reset your password:\n"
            f"{reset_link}\n\n"
            f"This link is valid for 1 hour."
        )
        await self.send_email(email, subject, body)


email_service = EmailService()
