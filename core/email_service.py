"""
CHAIRMAN - Email Service
Send verification codes and notifications via SMTP
"""
from __future__ import annotations

import smtplib
import secrets
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional

from core.logging_config import get_logger

logger = get_logger(__name__)


class EmailService:
    """Email sending service using SMTP."""

    def __init__(
        self,
        smtp_host: str = "",
        smtp_port: int = 587,
        smtp_user: str = "",
        smtp_password: str = "",
        from_email: str = "",
        from_name: str = "CHAIRMAN"
    ):
        """
        Initialize email service.

        Args:
            smtp_host: SMTP server hostname
            smtp_port: SMTP server port (587 for TLS, 465 for SSL)
            smtp_user: SMTP username
            smtp_password: SMTP password or app password
            from_email: Sender email address
            from_name: Sender display name
        """
        self.smtp_host = smtp_host
        self.smtp_port = smtp_port
        self.smtp_user = smtp_user
        self.smtp_password = smtp_password
        self.from_email = from_email or smtp_user
        self.from_name = from_name
        self._configured = bool(smtp_host and smtp_user and smtp_password)

    @classmethod
    def from_config(cls) -> 'EmailService':
        """Create email service from config file or environment."""
        try:
            from config import EmailConfig
            return cls(
                smtp_host=EmailConfig.SMTP_HOST,
                smtp_port=EmailConfig.SMTP_PORT,
                smtp_user=EmailConfig.SMTP_USER,
                smtp_password=EmailConfig.SMTP_PASSWORD,
                from_email=EmailConfig.FROM_EMAIL,
                from_name=EmailConfig.FROM_NAME
            )
        except (ImportError, AttributeError):
            logger.warning("Email config not found, email service disabled")
            return cls()

    def is_configured(self) -> bool:
        """Check if email service is properly configured."""
        return self._configured

    def generate_verification_code(self) -> str:
        """Generate a 6-digit verification code."""
        return f"{secrets.randbelow(1000000):06d}"

    def send_verification_email(self, to_email: str, code: str) -> tuple[bool, str]:
        """
        Send a verification code email.

        Args:
            to_email: Recipient email address
            code: 6-digit verification code

        Returns:
            Tuple of (success, message)
        """
        if not self._configured:
            logger.warning(f"Email not configured. Verification code for {to_email}: {code}")
            return False, "Email service not configured"

        subject = "Your CHAIRMAN Verification Code"
        html_body = f"""
        <html>
        <body style="font-family: Arial, sans-serif; background-color: #121212; padding: 40px;">
            <div style="max-width: 500px; margin: 0 auto; background-color: #1E1E1E; border-radius: 12px; padding: 40px;">
                <h1 style="color: #5865F2; text-align: center; letter-spacing: 3px; margin-bottom: 30px;">CHAIRMAN</h1>
                <p style="color: #FFFFFF; font-size: 16px; text-align: center;">Your verification code is:</p>
                <div style="background-color: #252525; border-radius: 8px; padding: 20px; margin: 20px 0;">
                    <p style="color: #5865F2; font-size: 32px; font-weight: bold; text-align: center; letter-spacing: 8px; margin: 0;">{code}</p>
                </div>
                <p style="color: #888888; font-size: 14px; text-align: center;">This code expires in 10 minutes.</p>
                <p style="color: #666666; font-size: 12px; text-align: center; margin-top: 30px;">If you didn't request this code, please ignore this email.</p>
            </div>
        </body>
        </html>
        """

        text_body = f"""
        CHAIRMAN - Verification Code

        Your verification code is: {code}

        This code expires in 10 minutes.

        If you didn't request this code, please ignore this email.
        """

        return self._send_email(to_email, subject, text_body, html_body)

    def _send_email(
        self,
        to_email: str,
        subject: str,
        text_body: str,
        html_body: Optional[str] = None
    ) -> tuple[bool, str]:
        """
        Send an email.

        Args:
            to_email: Recipient email address
            subject: Email subject
            text_body: Plain text body
            html_body: Optional HTML body

        Returns:
            Tuple of (success, message)
        """
        try:
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = f"{self.from_name} <{self.from_email}>"
            msg['To'] = to_email

            msg.attach(MIMEText(text_body, 'plain'))
            if html_body:
                msg.attach(MIMEText(html_body, 'html'))

            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_user, self.smtp_password)
                server.send_message(msg)

            logger.info(f"Email sent to {to_email}")
            return True, "Email sent successfully"

        except smtplib.SMTPAuthenticationError:
            logger.error("SMTP authentication failed")
            return False, "Email authentication failed"
        except smtplib.SMTPException as e:
            logger.error(f"SMTP error: {e}")
            return False, f"Failed to send email: {str(e)}"
        except Exception as e:
            logger.error(f"Email error: {e}")
            return False, f"Email error: {str(e)}"
