from __future__ import annotations

import os
import smtplib
from dataclasses import dataclass
from email.message import EmailMessage
from pathlib import Path
from typing import Optional

from loguru import logger

from utils.io_safe import write_text


@dataclass
class EmailSettings:
    host: str
    port: int
    username: str | None
    password: str | None
    mail_to: str
    mail_from: str
    attach_summary: bool = True


class EmailTransportError(RuntimeError):
    pass


def build_email_subject(prefix: str, report_date: str) -> str:
    return f"{prefix} {report_date}".strip()


def build_body(report_date: str, generated_at: str) -> str:
    return (
        f"Drupal Weekly for {report_date} attached.\n"
        f"Generated at {generated_at}.\n"
        "Sources: drupal.org verified.\n"
    )


def send_email(
    settings: EmailSettings,
    subject: str,
    body: str,
    summary_path: Path | None,
    summary_text: str | None,
    summary_pdf_path: Path | None,
) -> None:
    logger.info("[email_sender] preparing email for {}", settings.mail_to)
    msg = EmailMessage()
    msg["Subject"] = subject
    msg["To"] = settings.mail_to
    msg["From"] = settings.mail_from
    msg.set_content(body)

    if settings.attach_summary and summary_text is not None:
        msg.add_attachment(summary_text, subtype="markdown", maintype="text", filename="summary.md")
    elif summary_path and summary_path.exists():
        msg.add_attachment(summary_path.read_text(encoding="utf-8"), subtype="markdown", maintype="text", filename=summary_path.name)

    if summary_pdf_path and summary_pdf_path.exists():
        msg.add_attachment(
            summary_pdf_path.read_bytes(),
            maintype="application",
            subtype="pdf",
            filename=summary_pdf_path.name,
        )

    try:
        with smtplib.SMTP(settings.host, settings.port, timeout=30) as smtp:
            if settings.username and settings.password:
                smtp.starttls()
                smtp.login(settings.username, settings.password)
            smtp.send_message(msg)
        logger.info("[email_sender] email sent")
    except Exception as exc:  # pragma: no cover - network call
        logger.error("[email_sender] failed: {}", exc)
        raise EmailTransportError("Failed to send email") from exc


def discover_email_settings(env: dict[str, str], attach_summary: bool) -> EmailSettings:
    return EmailSettings(
        host=env.get("SMTP_HOST", ""),
        port=int(env.get("SMTP_PORT", "25")),
        username=env.get("SMTP_USER") or None,
        password=env.get("SMTP_PASS") or None,
        mail_to=env.get("MAIL_TO", ""),
        mail_from=env.get("MAIL_FROM", "Drupal Weekly <noreply@example.com>"),
        attach_summary=attach_summary,
    )
