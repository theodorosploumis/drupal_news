"""Email sender for Drupal Newsletter."""
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from pathlib import Path
from typing import Optional
import os


def send_email(
    smtp_host: str,
    smtp_port: int,
    smtp_user: str,
    smtp_pass: str,
    mail_from: str,
    mail_to: str,
    subject: str,
    body: str,
    attachment_path: Optional[Path] = None,
    timeout: int = 30
) -> bool:
    """
    Send email with optional attachment.

    Args:
        smtp_host: SMTP server hostname
        smtp_port: SMTP port
        smtp_user: SMTP username
        smtp_pass: SMTP password
        mail_from: From address
        mail_to: To address
        subject: Email subject
        body: Email body
        attachment_path: Optional path to attachment file
        timeout: Connection timeout in seconds (default: 30)

    Returns:
        True if sent successfully, False otherwise
    """
    try:
        # Create message
        msg = MIMEMultipart()
        msg['From'] = mail_from
        msg['To'] = mail_to
        msg['Subject'] = subject

        # Add body
        msg.attach(MIMEText(body, 'plain'))

        # Add attachment if provided
        if attachment_path and Path(attachment_path).exists():
            with open(attachment_path, 'rb') as f:
                part = MIMEBase('application', 'octet-stream')
                part.set_payload(f.read())
                encoders.encode_base64(part)
                part.add_header(
                    'Content-Disposition',
                    f'attachment; filename={Path(attachment_path).name}'
                )
                msg.attach(part)

        # Connect and send with timeout
        with smtplib.SMTP(smtp_host, smtp_port, timeout=timeout) as server:
            server.starttls()
            server.login(smtp_user, smtp_pass)
            server.send_message(msg)

        return True

    except smtplib.SMTPAuthenticationError as e:
        print(f"Email authentication failed: {e}")
        print("For Gmail, you need to use an App Password: https://support.google.com/accounts/answer/185833")
        return False
    except smtplib.SMTPException as e:
        print(f"SMTP error: {e}")
        return False
    except TimeoutError as e:
        print(f"Email timeout after {timeout}s: {e}")
        return False
    except Exception as e:
        print(f"Email sending failed: {e}")
        return False


def send_report(
    config: dict,
    env: dict,
    run_date: str,
    summary_path: Path,
    timezone: str,
    period_label: str = "Weekly"
) -> bool:
    """
    Send Drupal report email.

    Args:
        config: Configuration dictionary
        env: Environment variables dictionary
        run_date: Run date string (YYYY-MM-DD)
        summary_path: Path to summary.md file
        timezone: Timezone name
        period_label: Period label (e.g., "Weekly", "Biweekly")

    Returns:
        True if sent successfully
    """
    subject_prefix = config.get("email", {}).get("subject_prefix", f"[Drupal {period_label}]")
    subject = f"{subject_prefix} {run_date}"

    body = f"""
        Generation date: {run_date} ({timezone}).
        Agreegator period: {period_label}
    """

    # Get attachment path if enabled
    attachment = None
    if config.get("email", {}).get("attach_summary", True):
        # Check for attachment format preference (pdf or md)
        attachment_format = config.get("email", {}).get("attachment_format", "pdf")

        run_dir = summary_path.parent

        if attachment_format == "pdf":
            # Prefer PDF if it exists
            pdf_path = run_dir / "summary.pdf"
            if pdf_path.exists():
                attachment = pdf_path
            else:
                # Fall back to markdown if PDF doesn't exist
                attachment = summary_path
        else:
            # Use markdown
            attachment = summary_path

    # Get timeout from env or use default
    timeout = int(env.get("SMTP_TIMEOUT", 30))

    return send_email(
        smtp_host=env.get("SMTP_HOST"),
        smtp_port=int(env.get("SMTP_PORT", 587)),
        smtp_user=env.get("SMTP_USER"),
        smtp_pass=env.get("SMTP_PASS"),
        mail_from=env.get("MAIL_FROM"),
        mail_to=env.get("MAIL_TO"),
        subject=subject,
        body=body,
        attachment_path=attachment,
        timeout=timeout
    )


def write_email_log(
    output_path: Path,
    subject: str,
    body: str,
    mail_to: str,
    sent: bool,
    attachment: str = None
):
    """
    Write email log file.

    Args:
        output_path: Path to email.txt
        subject: Email subject
        body: Email body
        mail_to: Recipient address
        sent: Whether email was sent successfully
        attachment: Optional attachment filename
    """
    log_content = f"""Email Log
=========

Subject: {subject}
To: {mail_to}
Status: {"Sent" if sent else "Failed"}
"""

    if attachment:
        log_content += f"Attachment: {attachment}\n"

    log_content += f"""
Body:
{body}
"""

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(log_content)
