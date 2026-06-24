"""
Email utilities for sending verification and reset messages.
"""

import logging
from typing import Optional

import httpx

from app.core.config import settings


logger = logging.getLogger(__name__)


class EmailSendError(Exception):
    pass


async def send_email(
    to_email: str,
    subject: str,
    html_body: str,
    text_body: Optional[str] = None,
) -> None:
    """Send an email using Resend if configured, otherwise log to console."""
    if settings.RESEND_API_KEY:
        payload = {
            "from": f"{settings.EMAIL_FROM_NAME} <{settings.EMAIL_FROM}>",
            "to": [to_email],
            "subject": subject,
            "html": html_body,
        }
        if text_body:
            payload["text"] = text_body

        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(
                "https://api.resend.com/emails",
                json=payload,
                headers={
                    "Authorization": f"Bearer {settings.RESEND_API_KEY}",
                    "Content-Type": "application/json",
                },
            )
            if response.status_code >= 300:
                raise EmailSendError(
                    f"Failed to send email via Resend: {response.status_code} {response.text}"
                )
        return

    # Fallback developer logging
    logger.info(
        "Email debug — to=%s subject=%s body=%s",
        to_email,
        subject,
        text_body or html_body,
    )
