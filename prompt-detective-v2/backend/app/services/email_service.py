"""Email service utilities using Brevo API (free, no domain needed) or SMTP fallback."""
import asyncio
import html
import smtplib
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Optional

from ..core.config import settings


def get_email_template_header() -> str:
    """Common email header shared across templates."""
    return """
    <!-- Header -->
    <div style="background: linear-gradient(135deg, #8B5CF6 0%, #3B82F6 100%); padding: 40px 20px; text-align: center; border-radius: 10px 10px 0 0;">
        <h1 style="color: #ffffff; margin: 0; font-size: 32px; font-weight: bold;">
            🔍 Prompt Detective
        </h1>
        <p style="color: #E9D5FF; margin: 10px 0 0 0; font-size: 16px;">
            AI-Powered Video & Image Analysis
        </p>
    </div>
    """


def get_email_template_footer() -> str:
    """Common email footer shared across templates."""
    return """
    <!-- Footer -->
    <div style="background-color: #F3F4F6; padding: 30px 20px; text-align: center; border-radius: 0 0 10px 10px; margin-top: 30px;">
        <p style="color: #6B7280; font-size: 14px; margin: 0 0 10px 0;">
            Made with ❤️ in India for creators worldwide
        </p>
        <p style="color: #6B7280; font-size: 12px; margin: 0 0 15px 0;">
            🇮🇳 Pricing optimized for Indian market | Daily limits that reset at midnight IST
        </p>
        <div style="margin: 15px 0;">
            <a href="https://prompt-detective.vercel.app" style="color: #8B5CF6; text-decoration: none; margin: 0 10px;">Website</a>
            <a href="https://prompt-detective.vercel.app/pricing" style="color: #8B5CF6; text-decoration: none; margin: 0 10px;">Pricing</a>
            <a href="https://prompt-detective.vercel.app/help" style="color: #8B5CF6; text-decoration: none; margin: 0 10px;">Help</a>
        </div>
        <p style="color: #9CA3AF; font-size: 11px; margin: 15px 0 0 0;">
            © 2025 Prompt Detective. All rights reserved.
        </p>
    </div>
    """


async def _send_with_brevo(
    *,
    to_email: str,
    subject: str,
    html: str,
    text: str,
    sender_name: Optional[str] = None,
    sender_email: Optional[str] = None,
) -> bool:
    """
    Send email using Brevo (Sendinblue) API
    - FREE 300 emails/day
    - No domain verification needed
    - Works with any email address
    - HTTPS-based (no port blocking on Render)
    """
    try:
        import sib_api_v3_sdk
        from sib_api_v3_sdk.rest import ApiException
        
        # Configure API key
        configuration = sib_api_v3_sdk.Configuration()
        configuration.api_key['api-key'] = settings.BREVO_API_KEY
        
        # Create API instance
        api_instance = sib_api_v3_sdk.TransactionalEmailsApi(
            sib_api_v3_sdk.ApiClient(configuration)
        )
        
        sender_name = sender_name or settings.EMAIL_FROM_NAME or "Reverse AI"
        sender_email = sender_email or settings.EMAIL_FROM_ADDRESS or "tryreverseai@gmail.com"
        
        # Create email
        send_smtp_email = sib_api_v3_sdk.SendSmtpEmail(
            to=[{"email": to_email}],
            sender={"name": sender_name, "email": sender_email},
            subject=subject,
            html_content=html,
            text_content=text
        )
        
        # Send email
        api_response = api_instance.send_transac_email(send_smtp_email)
        print(f"✅ Email sent via Brevo to {to_email} (Message ID: {api_response.message_id})")
        return True
        
    except ApiException as e:
        print(f"❌ Brevo API error for {to_email}: {e}")
        return False
    except Exception as exc:
        print(f"❌ Brevo send failed for {to_email}: {exc}")
        return False


async def _send_with_resend(
    *,
    to_email: str,
    subject: str,
    html: str,
    text: str,
    sender_name: Optional[str] = None,
    sender_email: Optional[str] = None,
) -> bool:
    """Send email using Resend API (HTTP-based, works on Render free tier)"""
    try:
        import resend
        
        resend.api_key = settings.RESEND_API_KEY
        
        sender_name = sender_name or settings.EMAIL_FROM_NAME or "Reverse AI"
        sender_email = sender_email or settings.EMAIL_FROM_ADDRESS or "onboarding@resend.dev"
        
        params = {
            "from": f"{sender_name} <{sender_email}>",
            "to": [to_email],
            "subject": subject,
            "html": html,
        }
        
        email = resend.Emails.send(params)
        print(f"✅ Email sent via Resend to {to_email} (ID: {email.get('id', 'N/A')})")
        return True
        
    except Exception as exc:
        print(f"❌ Resend send failed for {to_email}: {exc}")
        return False


def _send_with_smtp_sync(
    *,
    to_email: str,
    subject: str,
    html: str,
    text: str,
    sender_name: str,
    sender_email: str,
) -> None:
    provider = (settings.EMAIL_PROVIDER or "").lower()
    host = settings.SMTP_HOST or ("smtp.gmail.com" if provider == "gmail" else None)
    port = settings.SMTP_PORT or (587 if provider == "gmail" else 25)
    sender_name = sender_name.strip() if sender_name else sender_name
    sender_email = sender_email.strip() if sender_email else sender_email

    provider = (settings.EMAIL_PROVIDER or "").lower()
    username = (settings.SMTP_USERNAME or sender_email or "").strip()
    password = (settings.SMTP_PASSWORD or "").strip()
    if provider in {"gmail", "google"} and password:
        password = "".join(password.split())
    use_tls = settings.SMTP_USE_TLS

    if not host:
        raise ValueError("SMTP_HOST not configured. Please set SMTP_HOST environment variable.")
    if not password:
        raise ValueError("SMTP_PASSWORD not configured. Please set SMTP_PASSWORD environment variable.")
    if not username:
        raise ValueError("SMTP_USERNAME not configured. Please set SMTP_USERNAME environment variable.")

    message = MIMEMultipart("alternative")
    message["Subject"] = subject
    message["From"] = f"{sender_name} <{sender_email}>"
    message["To"] = to_email
    message.attach(MIMEText(text, "plain"))
    message.attach(MIMEText(html, "html"))

    try:
        with smtplib.SMTP(host, port, timeout=30) as server:
            if use_tls:
                server.starttls()
            if username and password:
                server.login(username, password)
            server.sendmail(sender_email, [to_email], message.as_string())
    except smtplib.SMTPAuthenticationError as e:
        raise ValueError(f"SMTP Authentication failed. Please check SMTP_USERNAME and SMTP_PASSWORD. Error: {e}")
    except smtplib.SMTPException as e:
        raise ValueError(f"SMTP error occurred: {e}")
    except Exception as e:
        raise ValueError(f"Failed to send email: {e}")


async def _send_with_smtp(**kwargs) -> bool:
    try:
        await asyncio.to_thread(_send_with_smtp_sync, **kwargs)
        print(f"✅ Email sent via SMTP to {kwargs['to_email']}")
        return True
    except Exception as exc:  # pragma: no cover - external SMTP failure
        import logging
        import traceback
        logger = logging.getLogger(__name__)
        error_msg = f"❌ SMTP send failed for {kwargs['to_email']}: {exc}"
        print(error_msg)
        logger.error(error_msg)
        logger.error(f"Full traceback: {traceback.format_exc()}")
        # Print detailed config for debugging (without password)
        print(f"SMTP Config: host={settings.SMTP_HOST}, port={settings.SMTP_PORT}, username={settings.SMTP_USERNAME}, use_tls={settings.SMTP_USE_TLS}")
        return False


async def _dispatch_email(
    *,
    to_email: str,
    subject: str,
    html: str,
    text: str,
    sender_name: Optional[str] = None,
    sender_email: Optional[str] = None,
) -> bool:
    """
    Send email using available service.
    Priority: Brevo (free, no domain) > Resend > SMTP
    """
    sender_name = sender_name or settings.EMAIL_FROM_NAME or "Reverse AI"
    sender_email = sender_email or settings.EMAIL_FROM_ADDRESS or "tryreverseai@gmail.com"
    
    # Priority 1: Brevo (FREE 300/day, no domain needed, works on Render)
    if settings.BREVO_API_KEY:
        print(f"📧 Attempting to send email via Brevo to {to_email}")
        success = await _send_with_brevo(
            to_email=to_email,
            subject=subject,
            html=html,
            text=text,
            sender_name=sender_name,
            sender_email=sender_email,
        )
        if success:
            return True
        print("⚠️ Brevo failed, trying next method...")
    
    # Priority 2: Resend (requires domain verification)
    if settings.RESEND_API_KEY:
        print(f"📧 Attempting to send email via Resend to {to_email}")
        success = await _send_with_resend(
            to_email=to_email,
            subject=subject,
            html=html,
            text=text,
            sender_name=sender_name,
            sender_email=sender_email,
        )
        if success:
            return True
        print("⚠️ Resend failed, trying SMTP fallback...")
    
    # Priority 3: SMTP (doesn't work on Render free tier)
    if settings.SMTP_PASSWORD:
        print(f"📧 Attempting to send email via SMTP to {to_email}")
        return await _send_with_smtp(
            to_email=to_email,
            subject=subject,
            html=html,
            text=text,
            sender_name=sender_name,
            sender_email=sender_email,
        )
    
    print(f"❌ No email service configured (need BREVO_API_KEY, RESEND_API_KEY, or SMTP_PASSWORD)")
    return False


async def send_contact_notification_email(
    *,
    admin_email: str,
    contact_name: str,
    contact_email: str,
    topic_label: str,
    topic_key: str,
    message_body: str,
    selected_question: str | None = None,
    metadata: dict[str, str] | None = None,
) -> bool:
    """Send an internal alert when a customer submits the contact form."""

    subject = f"📩 New Support Request · {topic_label}"

    safe_message = html.escape(message_body).replace("\n", "<br />") if message_body else "<em>No additional notes provided.</em>"
    safe_question = (
        f"<p style=\"margin: 6px 0;\"><strong>Pre-selected query</strong><br />{html.escape(selected_question)}</p>"
        if selected_question
        else ""
    )

    meta_rows = ""
    if metadata:
        for key, value in metadata.items():
            if value:
                meta_rows += (
                    "<tr>"
                    f"<td style=\"padding: 6px 12px; color: #6B7280; font-size: 14px;\">{html.escape(key)}</td>"
                    f"<td style=\"padding: 6px 12px; color: #111827; font-size: 14px; font-weight: 600;\">{html.escape(value)}</td>"
                    "</tr>"
                )

    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head><meta charset=\"utf-8\" /></head>
    <body style=\"margin:0; padding:24px; background-color:#F9FAFB; font-family: 'Inter', Arial, sans-serif;\">
        {get_email_template_header()}
        <div style=\"background-color:#ffffff; padding:32px;\">
            <h2 style=\"margin:0 0 16px; color:#111827; font-size:22px;\">New contact request</h2>
            <p style=\"color:#4B5563; font-size:15px; margin:0 0 24px;\">
                A customer just submitted the support form on Prompt Detective. Review the details below and respond within the target SLA.
            </p>
            <div style=\"background-color:#F9FAFB; border-radius:10px; padding:20px; border:1px solid #E5E7EB; margin-bottom:24px;\">
                <p style=\"margin:0; color:#6B7280; font-size:13px; text-transform:uppercase; letter-spacing:0.08em;\">Topic</p>
                <p style=\"margin:4px 0 0; color:#111827; font-size:18px; font-weight:600;\">{html.escape(topic_label)} <span style=\"color:#9CA3AF; font-size:13px; font-weight:400;\">({html.escape(topic_key)})</span></p>
            </div>
            <div style=\"border:1px solid #E5E7EB; border-radius:10px; overflow:hidden; margin-bottom:24px;\">
                <table style=\"width:100%; border-collapse:collapse;\">
                    <tr>
                        <td style=\"padding:12px 16px; background-color:#F3F4F6; color:#6B7280; font-size:13px; text-transform:uppercase; letter-spacing:0.08em;\">Customer</td>
                        <td style=\"padding:12px 16px; background-color:#F9FAFB; color:#111827; font-size:15px; font-weight:600;\">{html.escape(contact_name)} ({html.escape(contact_email)})</td>
                    </tr>
                    {meta_rows}
                </table>
            </div>
            <div style=\"border-left:4px solid #8B5CF6; background-color:#F5F3FF; padding:18px 20px; border-radius:10px;\">
                {safe_question}
                <p style=\"margin:12px 0 6px; color:#6B7280; font-size:13px; text-transform:uppercase; letter-spacing:0.08em;\">Customer notes</p>
                <div style=\"color:#1F2937; font-size:15px; line-height:1.6;\">{safe_message}</div>
            </div>
        </div>
        {get_email_template_footer()}
    </body>
    </html>
    """

    text_lines = [
        "New contact request",
        f"Topic: {topic_label} ({topic_key})",
        f"From: {contact_name} <{contact_email}>",
    ]
    if metadata:
        text_lines.append("Metadata:")
        for key, value in metadata.items():
            if value:
                text_lines.append(f"  - {key}: {value}")
    if selected_question:
        text_lines.append(f"Preferred question: {selected_question}")
    text_lines.append("Message:")
    text_lines.append(message_body or "(No additional notes provided)")

    text_content = "\n".join(text_lines)

    return await _dispatch_email(
        to_email=admin_email,
        subject=subject,
        html=html_content,
        text=text_content,
    )


async def send_contact_acknowledgement_email(
    *,
    contact_email: str,
    contact_name: str,
    topic_label: str,
    expected_response_hours: int,
) -> bool:
    """Send a polite acknowledgement to the customer after form submission."""

    subject = "🤝 We've received your request"

    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head><meta charset=\"utf-8\" /></head>
    <body style=\"margin:0; padding:24px; background-color:#F9FAFB; font-family: 'Inter', Arial, sans-serif;\">
        {get_email_template_header()}
        <div style=\"background-color:#ffffff; padding:32px;\">
            <h2 style=\"margin:0 0 16px; color:#111827; font-size:22px;\">Thanks for reaching out, {html.escape(contact_name)} 👋</h2>
            <p style=\"color:#4B5563; font-size:15px; line-height:1.7;\">
                We received your request about <strong>{html.escape(topic_label)}</strong> and passed it to the right team.
                You can expect a response within <strong>{expected_response_hours} hours</strong> (usually much sooner during business hours).
            </p>
            <div style=\"margin:24px 0; background-color:#F9FAFB; border-radius:12px; padding:20px; border:1px solid #E5E7EB;\">
                <p style=\"margin:0 0 8px; color:#6B7280; font-size:13px; text-transform:uppercase; letter-spacing:0.08em;\">Need to add anything?</p>
                <p style=\"margin:0; color:#374151; font-size:14px; line-height:1.6;\">
                    Reply directly to this email and it will reach the same support thread.
                    We're here Monday to Friday, 9:00–19:00 IST.
                </p>
            </div>
            <p style=\"color:#6B7280; font-size:13px; line-height:1.6;\">
                — Team Prompt Detective
            </p>
        </div>
        {get_email_template_footer()}
    </body>
    </html>
    """

    text_content = (
        f"Hi {contact_name},\n\n"
        f"We've received your request about {topic_label}. Our team will respond within {expected_response_hours} hours.\n\n"
        "If you need to add more details, just reply to this email.\n\n"
        "— Team Prompt Detective"
    )

    return await _dispatch_email(
        to_email=contact_email,
        subject=subject,
        html=html_content,
        text=text_content,
    )


async def send_waitlist_confirmation_email(
    *,
    contact_email: str,
    plan_name: str | None,
    source: str | None,
    already_joined: bool,
) -> bool:
    """Send acknowledgement to waitlist subscribers."""

    friendly_plan = plan_name.title() if plan_name else "upcoming"  # pragma: no cover - simple formatting
    subject = "✨ You're on the Prompt Detective waitlist"

    greeting_line = "You're already on our radar." if already_joined else "Thanks for reserving your spot."
    next_steps_line = (
        "We'll email you as soon as new seats open—expect rollout updates and yearly savings tips in your inbox."
        if not already_joined
        else "Sit tight while we put the finishing touches on things."
    )

    source_hint = f"We captured this from: {source}" if source else ""

    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head><meta charset=\"utf-8\" /></head>
    <body style=\"margin:0; padding:24px; background-color:#F9FAFB; font-family: 'Inter', Arial, sans-serif;\">
        {get_email_template_header()}
        <div style=\"background-color:#ffffff; padding:32px;\">
            <h2 style=\"margin:0 0 12px; color:#111827; font-size:22px;\">{greeting_line}</h2>
            <p style=\"margin:0 0 16px; color:#4B5563; font-size:15px; line-height:1.7;\">
                You've joined the waitlist for our <strong>{friendly_plan}</strong> release. {next_steps_line}
            </p>
            <div style=\"margin:24px 0; background-color:#F9FAFB; border-radius:12px; padding:20px; border:1px solid #E5E7EB;\">
                <p style=\"margin:0; color:#6B7280; font-size:13px; text-transform:uppercase; letter-spacing:0.08em;\">What's next</p>
                <ul style=\"margin:12px 0 0; padding-left:20px; color:#374151; font-size:14px; line-height:1.6;\">
                    <li>Early access invites roll out in waves once testing wraps.</li>
                    <li>We'll share setup guides, plan comparison charts, and special pricing.</li>
                    <li>Reply to this email if you'd like to book a kickoff call.</li>
                </ul>
            </div>
            <p style=\"color:#6B7280; font-size:13px;\">{source_hint}</p>
        </div>
        {get_email_template_footer()}
    </body>
    </html>
    """

    text_content = "\n".join(
        [
            greeting_line,
            f"Waitlist plan: {friendly_plan}",
            "We'll keep you posted with rollout updates and best-value bundles.",
            source_hint,
        ]
    )

    return await _dispatch_email(
        to_email=contact_email,
        subject=subject,
        html=html_content,
        text=text_content,
    )


async def send_account_deletion_confirmation_email(*, email: str, name: str | None) -> bool:
    """Notify users that their account has been deleted."""

    subject = "Your Prompt Detective account has been deleted"
    display_name = name or "there"

    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head><meta charset=\"utf-8\" /></head>
    <body style=\"margin:0; padding:24px; background-color:#F9FAFB; font-family: 'Inter', Arial, sans-serif;\">
        {get_email_template_header()}
        <div style=\"background-color:#ffffff; padding:32px;\">
            <h2 style=\"margin:0 0 16px; color:#111827; font-size:22px;\">Goodbye for now, {html.escape(display_name)} 👋</h2>
            <p style=\"color:#4B5563; font-size:15px; line-height:1.7;\">
                This email confirms that your Prompt Detective account and associated analyses have been permanently deleted.
                If you change your mind, you're always welcome to create a fresh workspace.
            </p>
            <div style=\"margin:24px 0; background-color:#F9FAFB; border-radius:12px; padding:20px; border:1px solid #E5E7EB;\">
                <p style=\"margin:0; color:#6B7280; font-size:13px; text-transform:uppercase; letter-spacing:0.08em;\">What was removed</p>
                <ul style=\"margin:12px 0 0; padding-left:20px; color:#374151; font-size:14px; line-height:1.6;\">
                    <li>Account profile, usage history, analyses, and credit packs.</li>
                    <li>API keys and active subscriptions.</li>
                    <li>Support threads connected to this email.</li>
                </ul>
            </div>
            <p style=\"color:#6B7280; font-size:13px;\">Need to restore anything for compliance? Reply to this email within 7 days and we'll help if data is still recoverable.</p>
        </div>
        {get_email_template_footer()}
    </body>
    </html>
    """

    text_content = (
        "Your Prompt Detective account has been deleted. "
        "Analyses, usage history, plans, and API keys have been removed. "
        "Reply within 7 days if you require regulatory proof of deletion."
    )

    return await _dispatch_email(
        to_email=email,
        subject=subject,
        html=html_content,
        text=text_content,
    )


async def send_verification_email(email: str, name: str, otp_code: str) -> bool:
    """Send email verification OTP."""
    subject = "🔐 Verify Your Prompt Detective Account"

    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
    </head>
    <body style="margin: 0; padding: 20px; background-color: #F9FAFB;">
        {get_email_template_header()}
        <!-- Content -->
        <div style="padding: 40px 30px; background-color: #ffffff;">
            <h2 style="color: #111827; margin: 0 0 20px 0; font-size: 24px;">
                Welcome to Prompt Detective! 👋
            </h2>
            <p style="color: #4B5563; font-size: 16px; line-height: 1.6; margin: 0 0 25px 0;">
                Hi <strong>{name}</strong>,
            </p>
            <p style="color: #4B5563; font-size: 16px; line-height: 1.6; margin: 0 0 25px 0;">
                Thank you for signing up! We're excited to have you on board. To complete your registration
                and start analyzing videos and images, please verify your email address.
            </p>
            <!-- OTP Box -->
            <div style="background: linear-gradient(135deg, #F3F4F6 0%, #E5E7EB 100%); border-left: 4px solid #8B5CF6; padding: 30px; border-radius: 8px; margin: 30px 0; text-align: center;">
                <p style="color: #6B7280; font-size: 14px; margin: 0 0 10px 0; text-transform: uppercase; letter-spacing: 1px;">
                    Your Verification Code
                </p>
                <div style="background-color: #ffffff; padding: 20px; border-radius: 8px; display: inline-block;">
                    <span style="font-size: 36px; font-weight: bold; letter-spacing: 8px; color: #8B5CF6; font-family: 'Courier New', monospace;">
                        {otp_code}
                    </span>
                </div>
                <p style="color: #9CA3AF; font-size: 13px; margin: 15px 0 0 0;">
                    ⏱️ This code expires in <strong>10 minutes</strong>
                </p>
            </div>
            <p style="color: #4B5563; font-size: 15px; line-height: 1.6; margin: 20px 0;">
                Enter this code on the verification page to activate your account.
            </p>
            <!-- What's Next Section -->
            <div style="background-color: #F9FAFB; padding: 25px; border-radius: 8px; margin: 30px 0;">
                <h3 style="color: #111827; margin: 0 0 15px 0; font-size: 18px;">
                    🚀 What's Next?
                </h3>
                <ul style="color: #4B5563; font-size: 14px; line-height: 1.8; margin: 0; padding-left: 20px;">
                    <li><strong>5 free analyses daily</strong> - Analyze images and get AI-generated prompts</li>
                    <li><strong>Video support</strong> - Upgrade to analyze video content (Starter plan at just ₹299/mo)</li>
                    <li><strong>API access</strong> - Integrate with your workflow (Pro plan at ₹699/mo)</li>
                    <li><strong>Daily reset model</strong> - Your limit resets every midnight IST</li>
                </ul>
            </div>
            <!-- Savings Tip -->
            <div style="background: linear-gradient(135deg, #8B5CF6 0%, #3B82F6 100%); padding: 25px; border-radius: 8px; margin: 30px 0; text-align: center;">
                <p style="color: #ffffff; font-size: 16px; margin: 0 0 10px 0; font-weight: bold;">
                    💡 Pro tip for later
                </p>
                <p style="color: #E9D5FF; font-size: 14px; margin: 0;">
                    Switch to yearly billing anytime to save <strong>17%</strong> instantly and unlock concierge onboarding when you upgrade.
                </p>
            </div>
            <!-- Security Notice -->
            <div style="background-color: #FEF3C7; border-left: 4px solid #F59E0B; padding: 15px; border-radius: 4px; margin: 30px 0;">
                <p style="color: #92400E; font-size: 13px; margin: 0; line-height: 1.6;">
                    🔒 <strong>Security Notice:</strong> Never share this code with anyone. Prompt Detective will never ask
                    for your OTP via phone or any other platform. If you didn't request this verification, please ignore this email.
                </p>
            </div>
        </div>
        {get_email_template_footer()}
    </body>
    </html>
    """

    text_content = f"""
    Welcome to Prompt Detective!

    Hi {name},

    Thank you for signing up! To complete your registration, please verify your email address.

    Your Verification Code: {otp_code}

    This code expires in 10 minutes.

    What's Next?
    - 5 free analyses daily
    - Video support available on Starter plan (₹299/mo)
    - API access on Pro plan (₹699/mo)
    - Daily reset limits that refresh at midnight IST

    Savings tip:
    Switch to yearly billing anytime to save 17% instantly and unlock concierge onboarding when you upgrade.

    Security Notice: Never share this code with anyone.

    © 2025 Prompt Detective. All rights reserved.
    """

    sent = await _dispatch_email(
        to_email=email,
        subject=subject,
        html=html_content,
        text=text_content,
    )

    if not sent:
        print("⚠️ Verification email not sent; printing OTP for debugging")
        print(f"Verification OTP for {email}: {otp_code}")
    return sent


async def send_password_reset_otp_email(email: str, name: str, otp_code: str) -> bool:
    """Send password reset OTP."""
    subject = "🔐 Reset Your Prompt Detective Password"

    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
    </head>
    <body style="margin: 0; padding: 20px; background-color: #F9FAFB;">
        {get_email_template_header()}
        <!-- Content -->
        <div style="padding: 40px 30px; background-color: #ffffff;">
            <h2 style="color: #111827; margin: 0 0 20px 0; font-size: 24px;">
                Password Reset Request 🔑
            </h2>
            <p style="color: #4B5563; font-size: 16px; line-height: 1.6; margin: 0 0 25px 0;">
                Hi <strong>{name}</strong>,
            </p>
            <p style="color: #4B5563; font-size: 16px; line-height: 1.6; margin: 0 0 25px 0;">
                We received a request to reset your password for your Prompt Detective account.
                Use the code below to reset your password.
            </p>
            <!-- OTP Box -->
            <div style="background: linear-gradient(135deg, #FEF3C7 0%, #FDE68A 100%); border-left: 4px solid #F59E0B; padding: 30px; border-radius: 8px; margin: 30px 0; text-align: center;">
                <p style="color: #92400E; font-size: 14px; margin: 0 0 10px 0; text-transform: uppercase; letter-spacing: 1px;">
                    Your Password Reset Code
                </p>
                <div style="background-color: #ffffff; padding: 20px; border-radius: 8px; display: inline-block;">
                    <span style="font-size: 36px; font-weight: bold; letter-spacing: 8px; color: #F59E0B; font-family: 'Courier New', monospace;">
                        {otp_code}
                    </span>
                </div>
                <p style="color: #92400E; font-size: 13px; margin: 15px 0 0 0;">
                    ⏱️ This code expires in <strong>10 minutes</strong>
                </p>
            </div>
            <p style="color: #4B5563; font-size: 15px; line-height: 1.6; margin: 20px 0;">
                Enter this code on the password reset page, then create a new strong password.
            </p>
            <!-- Security Tips -->
            <div style="background-color: #F0F9FF; padding: 25px; border-radius: 8px; margin: 30px 0; border-left: 4px solid #3B82F6;">
                <h3 style="color: #1E40AF; margin: 0 0 15px 0; font-size: 16px;">
                    🛡️ Security Tips for Strong Passwords
                </h3>
                <ul style="color: #1E3A8A; font-size: 14px; line-height: 1.8; margin: 0; padding-left: 20px;">
                    <li>Use at least 8 characters</li>
                    <li>Mix uppercase and lowercase letters</li>
                    <li>Include numbers and special characters</li>
                    <li>Avoid using personal information</li>
                    <li>Don't reuse passwords from other sites</li>
                </ul>
            </div>
            <!-- Did Not Request Section -->
            <div style="background-color: #FEE2E2; border-left: 4px solid #EF4444; padding: 15px; border-radius: 4px; margin: 30px 0;">
                <p style="color: #991B1B; font-size: 14px; margin: 0; line-height: 1.6;">
                    ❗ <strong>Didn't request a password reset?</strong><br>
                    If you didn't request this, please ignore this email and your password will remain unchanged.
                    Your account is secure. Consider changing your password if you suspect unauthorized access.
                </p>
            </div>
            <!-- Quick Access -->
            <div style="text-align: center; margin: 30px 0;">
                <a href="https://prompt-detective.vercel.app/reset-password"
                   style="display: inline-block; background: linear-gradient(135deg, #8B5CF6 0%, #3B82F6 100%);
                          color: #ffffff; text-decoration: none; padding: 15px 40px; border-radius: 8px;
                          font-weight: bold; font-size: 16px;">
                    Reset Password Now →
                </a>
            </div>
        </div>
        {get_email_template_footer()}
    </body>
    </html>
    """

    text_content = f"""
    Password Reset Request

    Hi {name},

    We received a request to reset your password for your Prompt Detective account.

    Your Password Reset Code: {otp_code}

    This code expires in 10 minutes.

    Enter this code on the password reset page, then create a new strong password.

    Security Tips:
    - Use at least 8 characters
    - Mix uppercase and lowercase letters
    - Include numbers and special characters

    Didn't request a password reset?
    If you didn't request this, please ignore this email. Your account is secure.

    © 2025 Prompt Detective. All rights reserved.
    """

    sent = await _dispatch_email(
        to_email=email,
        subject=subject,
        html=html_content,
        text=text_content,
    )

    if not sent:
        print("⚠️ Password reset email not sent; printing OTP for debugging")
        print(f"Password reset OTP for {email}: {otp_code}")
    return sent


async def send_welcome_email(email: str, name: str) -> bool:
    """Send welcome email after successful verification."""
    subject = "🎉 Welcome to Prompt Detective - Let's Get Started!"

    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
    </head>
    <body style="margin: 0; padding: 20px; background-color: #F9FAFB;">
        {get_email_template_header()}
        <!-- Content -->
        <div style="padding: 40px 30px; background-color: #ffffff;">
            <h2 style="color: #111827; margin: 0 0 20px 0; font-size: 28px; text-align: center;">
                🎉 Account Verified Successfully!
            </h2>
            <p style="color: #4B5563; font-size: 16px; line-height: 1.6; margin: 0 0 25px 0;">
                Hi <strong>{name}</strong>,
            </p>
            <p style="color: #4B5563; font-size: 16px; line-height: 1.6; margin: 0 0 25px 0;">
                Congratulations! Your email has been verified and your Prompt Detective account is now active.
                You're all set to start reverse-engineering images and videos with AI! 🚀
            </p>
            <!-- Quick Start Guide -->
            <div style="background: linear-gradient(135deg, #F0F9FF 0%, #E0F2FE 100%); padding: 30px; border-radius: 12px; margin: 30px 0;">
                <h3 style="color: #0C4A6E; margin: 0 0 20px 0; font-size: 20px; text-align: center;">
                    🚀 Quick Start Guide
                </h3>
                <div style="margin: 20px 0;">
                    <div style="background-color: #ffffff; padding: 20px; border-radius: 8px; margin: 15px 0; border-left: 4px solid #3B82F6;">
                        <h4 style="color: #1E40AF; margin: 0 0 10px 0; font-size: 16px;">
                            1️⃣ Upload Your First Image
                        </h4>
                        <p style="color: #475569; font-size: 14px; margin: 0; line-height: 1.6;">
                            Go to your dashboard and upload any image. Our AI will analyze it and generate the exact prompt used to create it.
                        </p>
                    </div>
                    <div style="background-color: #ffffff; padding: 20px; border-radius: 8px; margin: 15px 0; border-left: 4px solid #8B5CF6;">
                        <h4 style="color: #6B21A8; margin: 0 0 10px 0; font-size: 16px;">
                            2️⃣ Explore Your Free Tier
                        </h4>
                        <p style="color: #475569; font-size: 14px; margin: 0; line-height: 1.6;">
                            You get <strong>5 free analyses per day</strong>. Your limit resets every midnight IST.
                        </p>
                    </div>
                    <div style="background-color: #ffffff; padding: 20px; border-radius: 8px; margin: 15px 0; border-left: 4px solid #10B981;">
                        <h4 style="color: #065F46; margin: 0 0 10px 0; font-size: 16px;">
                            3️⃣ Upgrade When Ready
                        </h4>
                        <p style="color: #475569; font-size: 14px; margin: 0; line-height: 1.6;">
                            Need more? Check out our Starter plan (₹199/mo - First 500 users) with video support and 15 daily analyses.
                        </p>
                    </div>
                </div>
            </div>
            <!-- Your Plan Details -->
            <div style="background-color: #F9FAFB; padding: 25px; border-radius: 8px; margin: 30px 0;">
                <h3 style="color: #111827; margin: 0 0 15px 0; font-size: 18px;">
                    📊 Your Free Plan Includes:
                </h3>
                <ul style="color: #4B5563; font-size: 15px; line-height: 2; margin: 0; padding-left: 20px;">
                    <li>✅ 5 analyses per day</li>
                    <li>✅ Image-to-prompt conversion</li>
                    <li>✅ Standard processing speed</li>
                    <li>✅ Basic prompt output</li>
                    <li>✅ Community forum access</li>
                    <li>✅ Email support</li>
                </ul>
            </div>
            <!-- CTA Buttons -->
            <div style="text-align: center; margin: 40px 0;">
                <a href="https://prompt-detective.vercel.app/dashboard"
                   style="display: inline-block; background: linear-gradient(135deg, #8B5CF6 0%, #3B82F6 100%);
                          color: #ffffff; text-decoration: none; padding: 16px 40px; border-radius: 10px;
                          font-weight: bold; font-size: 16px; margin: 10px;">
                    🎯 Go to Dashboard
                </a>
                <br>
                <a href="https://prompt-detective.vercel.app/pricing"
                   style="display: inline-block; background-color: #ffffff; color: #8B5CF6; text-decoration: none;
                          padding: 16px 40px; border-radius: 10px; font-weight: bold; font-size: 16px;
                          border: 2px solid #8B5CF6; margin: 10px;">
                    💰 View Pricing
                </a>
            </div>
            <!-- Upgrade Guidance -->
            <div style="background: linear-gradient(135deg, #EEF2FF 0%, #E0E7FF 100%); padding: 25px; border-radius: 8px; margin: 30px 0; text-align: center;">
                <h3 style="color: #312E81; margin: 0 0 10px 0; font-size: 18px;">
                    📈 Scale when you're ready
                </h3>
                <p style="color: #3730A3; font-size: 14px; margin: 0; line-height: 1.6;">
                    Upgrade to Starter, Pro, or Business for more daily analyses, faster processing, and API workflows.
                    Yearly subscriptions now include an automatic <strong>17% discount</strong> plus onboarding resources tailored to your team.
                </p>
            </div>
            <!-- Support -->
            <div style="text-align: center; margin: 30px 0; padding: 20px; background-color: #F9FAFB; border-radius: 8px;">
                <p style="color: #6B7280; font-size: 14px; margin: 0 0 10px 0;">
                    Need help getting started?
                </p>
                <p style="color: #8B5CF6; font-size: 15px; margin: 0; font-weight: bold;">
                    📧 Email us at support@promptdetective.com
                </p>
                <p style="color: #6B7280; font-size: 13px; margin: 10px 0 0 0;">
                    We respond within 48 hours (faster for paid plans)
                </p>
            </div>
        </div>
        {get_email_template_footer()}
    </body>
    </html>
    """

    text_content = f"""
    Welcome to Prompt Detective!

    Hi {name},

    Congratulations! Your account is now active.

    Quick Start Guide:
    1. Upload Your First Image - Analyze any image and get AI-generated prompts
    2. Explore Your Free Tier - 5 analyses per day, resets at midnight IST
    3. Upgrade When Ready - Starter plan at ₹199/mo for first 500 users

    Your Free Plan Includes:
    - 5 analyses per day
    - Image-to-prompt conversion
    - Standard processing speed
    - Email support

    Scale when you're ready:
    Upgrade to paid plans for more daily analyses, faster processing, and API workflows. Yearly subscriptions save 17% automatically.

    Need help? Email us at support@promptdetective.com

    © 2025 Prompt Detective. All rights reserved.
    """

    sent = await _dispatch_email(
        to_email=email,
        subject=subject,
        html=html_content,
        text=text_content,
    )

    if not sent:
        print("⚠️ Welcome email failed to send")
    return sent


async def send_trial_started_email(email: str, name: str, plan: str, trial_ends: "datetime") -> bool:
    """Send trial started confirmation email."""
    from datetime import datetime, timezone
    
    subject = f"🎉 Your {plan.title()} Trial Has Started - 3 Days of Premium Features!"
    
    # Format trial end time
    trial_ends_str = trial_ends.strftime("%B %d, %Y at %I:%M %p IST")
    
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
    </head>
    <body style="margin: 0; padding: 20px; background-color: #F9FAFB;">
        {get_email_template_header()}
        <!-- Content -->
        <div style="padding: 40px 30px; background-color: #ffffff;">
            <h2 style="color: #111827; margin: 0 0 20px 0; font-size: 28px; text-align: center;">
                🚀 Your {plan.title()} Trial is Live!
            </h2>
            <p style="color: #4B5563; font-size: 16px; line-height: 1.6; margin: 0 0 25px 0;">
                Hi <strong>{name}</strong>,
            </p>
            <p style="color: #4B5563; font-size: 16px; line-height: 1.6; margin: 0 0 25px 0;">
                Great news! Your 3-day free trial of the <strong>{plan.title()} Plan</strong> has started.
                Enjoy all premium features with no credit card required! 🎉
            </p>
            <!-- Trial Timer -->
            <div style="background: linear-gradient(135deg, #10B981 0%, #059669 100%); padding: 30px; border-radius: 12px; margin: 30px 0; text-align: center;">
                <p style="color: #D1FAE5; font-size: 14px; margin: 0 0 10px 0; text-transform: uppercase; letter-spacing: 2px;">
                    Trial Active Until
                </p>
                <p style="color: #ffffff; font-size: 24px; font-weight: bold; margin: 0;">
                    {trial_ends_str}
                </p>
                <p style="color: #D1FAE5; font-size: 14px; margin: 15px 0 0 0;">
                    ⏰ After 3 days, you'll automatically be moved to the Free plan
                </p>
            </div>
            <!-- What You Get -->
            <div style="background-color: #F9FAFB; padding: 25px; border-radius: 8px; margin: 30px 0;">
                <h3 style="color: #111827; margin: 0 0 15px 0; font-size: 18px;">
                    ✨ Your {plan.title()} Trial Includes:
                </h3>
                <ul style="color: #4B5563; font-size: 15px; line-height: 2; margin: 0; padding-left: 20px;">
                    {"<li>📸 15 analyses per day</li>" if plan == "starter" else ""}
                    {"<li>📸 50 analyses per day</li>" if plan == "pro" else ""}
                    {"<li>📸 150 analyses per day</li>" if plan == "business" else ""}
                    <li>🎥 Video analysis support</li>
                    <li>⚡ Priority processing speed</li>
                    <li>🎨 Advanced prompt outputs</li>
                    {"<li>🔌 API access (5,000 calls/month)</li>" if plan in ["pro", "business"] else ""}
                    {"<li>🔌 API access (20,000 calls/month)</li>" if plan == "business" else ""}
                    {"<li>👨‍💼 Dedicated account manager</li>" if plan == "business" else ""}
                    <li>💬 Priority email support</li>
                </ul>
            </div>
            <!-- CTA -->
            <div style="text-align: center; margin: 40px 0;">
                <a href="https://prompt-detective.vercel.app/dashboard"
                   style="display: inline-block; background: linear-gradient(135deg, #8B5CF6 0%, #3B82F6 100%);
                          color: #ffffff; text-decoration: none; padding: 16px 40px; border-radius: 10px;
                          font-weight: bold; font-size: 16px; margin: 10px;">
                    🎯 Start Analyzing Now
                </a>
            </div>
            <!-- Important Notice -->
            <div style="background-color: #FEF3C7; border-left: 4px solid #F59E0B; padding: 20px; border-radius: 4px; margin: 30px 0;">
                <h4 style="color: #92400E; margin: 0 0 10px 0; font-size: 16px;">
                    📝 Important: What Happens After Trial?
                </h4>
                <p style="color: #78350F; font-size: 14px; margin: 0; line-height: 1.6;">
                    <strong>No automatic charges!</strong> After 3 days, you'll be automatically moved to our Free plan
                    (5 analyses/day). Upgrade anytime to keep premium features—and when you're ready, switch to yearly billing
                    to save <strong>17%</strong> instantly and unlock concierge onboarding.
                </p>
            </div>
        </div>
        {get_email_template_footer()}
    </body>
    </html>
    """
    
    text_content = f"""
    Your {plan.title()} Trial is Live!

    Hi {name},

    Your 3-day free trial of the {plan.title()} Plan has started.

    Trial Active Until: {trial_ends_str}

    After 3 days, you'll automatically be moved to the Free plan.

    What You Get:
    - Enhanced daily analyses
    - Video analysis support
    - Priority processing speed
    - Priority email support

    No automatic charges! Upgrade anytime to keep premium features. Switch to yearly later to save 17% and unlock concierge onboarding.

    © 2025 Prompt Detective. All rights reserved.
    """
    
    return await _dispatch_email(
        to_email=email,
        subject=subject,
        html=html_content,
        text=text_content,
    )


async def send_trial_expiring_soon_email(email: str, name: str, plan: str, hours_remaining: int, trial_ends: "datetime") -> bool:
    """Send trial expiring soon notification."""
    subject = f"⏰ Your {plan.title()} Trial Expires in {hours_remaining} Hours"
    
    trial_ends_str = trial_ends.strftime("%B %d at %I:%M %p IST")
    
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
    </head>
    <body style="margin: 0; padding: 20px; background-color: #F9FAFB;">
        {get_email_template_header()}
        <!-- Content -->
        <div style="padding: 40px 30px; background-color: #ffffff;">
            <h2 style="color: #111827; margin: 0 0 20px 0; font-size: 28px; text-align: center;">
                ⏰ Trial Ending Soon
            </h2>
            <p style="color: #4B5563; font-size: 16px; line-height: 1.6; margin: 0 0 25px 0;">
                Hi <strong>{name}</strong>,
            </p>
            <p style="color: #4B5563; font-size: 16px; line-height: 1.6; margin: 0 0 25px 0;">
                Your {plan.title()} trial is ending soon! You have only <strong>{hours_remaining} hours</strong> left
                to enjoy premium features before automatically moving to the Free plan.
            </p>
            <!-- Urgency Timer -->
            <div style="background: linear-gradient(135deg, #F59E0B 0%, #D97706 100%); padding: 30px; border-radius: 12px; margin: 30px 0; text-align: center;">
                <p style="color: #FEF3C7; font-size: 16px; margin: 0 0 10px 0; text-transform: uppercase; letter-spacing: 2px;">
                    Trial Ends On
                </p>
                <p style="color: #ffffff; font-size: 28px; font-weight: bold; margin: 0;">
                    {trial_ends_str}
                </p>
                <p style="color: #FEF3C7; font-size: 18px; font-weight: bold; margin: 15px 0 0 0;">
                    ⏳ Only {hours_remaining} Hours Left!
                </p>
            </div>
            <!-- Special Offer -->
            <div style="background: linear-gradient(135deg, #8B5CF6 0%, #3B82F6 100%); padding: 30px; border-radius: 12px; margin: 30px 0; text-align: center;">
                <h3 style="color: #ffffff; margin: 0 0 15px 0; font-size: 24px;">
                    💡 Keep Your Premium Flow Going
                </h3>
                <p style="color: #E9D5FF; font-size: 16px; margin: 0 0 16px 0; line-height: 1.6;">
                    Upgrade before the timer runs out to keep video analysis, faster processing, and higher limits.
                    Want the best value? Switch to yearly billing when you upgrade to save <strong>17%</strong> instantly
                    and unlock concierge onboarding on applicable plans.
                </p>
                {"<p style='color: #C4B5FD; font-size: 15px; margin: 12px 0 0 0;'>Starter is ₹299/mo — flip to yearly anytime and save 17%.</p>" if plan == "starter" else ""}
                {"<p style='color: #C4B5FD; font-size: 15px; margin: 12px 0 0 0;'>Pro is ₹699/mo — yearly saves 17% and adds priority onboarding.</p>" if plan == "pro" else ""}
                {"<p style='color: #C4B5FD; font-size: 15px; margin: 12px 0 0 0;'>Business is ₹1,499/mo — yearly saves 17% plus white-glove setup.</p>" if plan == "business" else ""}
            </div>
            <!-- CTA -->
            <div style="text-align: center; margin: 40px 0;">
                <a href="https://prompt-detective.vercel.app/pricing"
                   style="display: inline-block; background: linear-gradient(135deg, #10B981 0%, #059669 100%);
                          color: #ffffff; text-decoration: none; padding: 18px 50px; border-radius: 10px;
                          font-weight: bold; font-size: 18px; margin: 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
                    ✨ Upgrade Now
                </a>
            </div>
            <!-- What You'll Keep -->
            <div style="background-color: #F9FAFB; padding: 25px; border-radius: 8px; margin: 30px 0;">
                <h3 style="color: #111827; margin: 0 0 15px 0; font-size: 18px;">
                    🎯 Keep These Premium Features:
                </h3>
                <ul style="color: #4B5563; font-size: 15px; line-height: 2; margin: 0; padding-left: 20px;">
                    {"<li>📸 15 analyses/day (vs 5 on Free)</li>" if plan == "starter" else ""}
                    {"<li>📸 50 analyses/day (vs 5 on Free)</li>" if plan == "pro" else ""}
                    {"<li>📸 150 analyses/day (vs 5 on Free)</li>" if plan == "business" else ""}
                    <li>🎥 Video analysis (not on Free)</li>
                    <li>⚡ 5x faster processing</li>
                    <li>🎨 Advanced AI prompts</li>
                    <li>💬 Priority support</li>
                </ul>
            </div>
        </div>
        {get_email_template_footer()}
    </body>
    </html>
    """
    
    text_content = f"""
    Trial Ending Soon

    Hi {name},

    Your {plan.title()} trial is ending soon! Only {hours_remaining} hours left.

    Trial Ends On: {trial_ends_str}

    Upgrade now to keep premium tools active.
    Switch to yearly billing anytime to save 17% and get concierge onboarding support.

    Keep Premium Features:
    - Enhanced daily analyses
    - Video analysis support
    - 5x faster processing
    - Priority support

    Upgrade now: https://prompt-detective.vercel.app/pricing

    © 2025 Prompt Detective. All rights reserved.
    """
    
    return await _dispatch_email(
        to_email=email,
        subject=subject,
        html=html_content,
        text=text_content,
    )


async def send_trial_expired_email(email: str, name: str, trial_plan: str) -> bool:
    """Send trial expired notification."""
    subject = "Your Trial Has Ended - You're Now on the Free Plan"
    
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
    </head>
    <body style="margin: 0; padding: 20px; background-color: #F9FAFB;">
        {get_email_template_header()}
        <!-- Content -->
        <div style="padding: 40px 30px; background-color: #ffffff;">
            <h2 style="color: #111827; margin: 0 0 20px 0; font-size: 24px; text-align: center;">
                Your {trial_plan.title()} Trial Has Ended
            </h2>
            <p style="color: #4B5563; font-size: 16px; line-height: 1.6; margin: 0 0 25px 0;">
                Hi <strong>{name}</strong>,
            </p>
            <p style="color: #4B5563; font-size: 16px; line-height: 1.6; margin: 0 0 25px 0;">
                Your 3-day trial of the {trial_plan.title()} Plan has ended. We hope you enjoyed exploring our premium features!
                You've been automatically moved to our <strong>Free Plan</strong> and can continue using Prompt Detective.
            </p>
            <!-- Current Plan -->
            <div style="background-color: #F9FAFB; padding: 25px; border-radius: 8px; margin: 30px 0; text-align: center;">
                <h3 style="color: #111827; margin: 0 0 15px 0; font-size: 18px;">
                    📊 Your Current Plan: Free
                </h3>
                <ul style="color: #4B5563; font-size: 15px; line-height: 2; margin: 0; padding-left: 20px; text-align: left; display: inline-block;">
                    <li>✅ 5 analyses per day</li>
                    <li>✅ Image-to-prompt conversion</li>
                    <li>✅ Standard processing speed</li>
                    <li>✅ Email support</li>
                </ul>
            </div>
            <!-- Upgrade Offer -->
            <div style="background: linear-gradient(135deg, #8B5CF6 0%, #3B82F6 100%); padding: 30px; border-radius: 12px; margin: 30px 0; text-align: center;">
                <h3 style="color: #ffffff; margin: 0 0 15px 0; font-size: 24px;">
                    🚀 Ready to Keep the Pro Tools?
                </h3>
                <p style="color: #E9D5FF; font-size: 16px; margin: 0 0 16px 0; line-height: 1.6;">
                    Upgrade whenever you're ready to reactivate premium features. Prefer the best value?
                    Yearly billing saves <strong>17%</strong> instantly and includes concierge onboarding on Pro and Business plans.
                </p>
                <p style="color: #C4B5FD; font-size: 14px; margin: 12px 0 0 0;">
                    Monthly plans start at ₹299. You can switch to yearly inside your dashboard anytime.
                </p>
                <a href="https://prompt-detective.vercel.app/pricing"
                   style="display: inline-block; background-color: #ffffff; color: #8B5CF6; text-decoration: none;
                          padding: 16px 40px; border-radius: 10px; font-weight: bold; font-size: 16px; margin: 18px 10px 0;">
                    ✨ Explore Plans
                </a>
            </div>
        </div>
        {get_email_template_footer()}
    </body>
    </html>
    """
    
    text_content = f"""
    Your {trial_plan.title()} Trial Has Ended

    Hi {name},

    Your 3-day trial has ended. You've been moved to our Free Plan.

    Your Current Plan: Free
    - 5 analyses per day
    - Image-to-prompt conversion
    - Email support

    Upgrade anytime to reactivate premium features. Monthly plans start at ₹299.
    Switch to yearly billing when you're ready to save 17% and unlock concierge onboarding on higher tiers.

    Explore plans: https://prompt-detective.vercel.app/pricing

    © 2025 Prompt Detective. All rights reserved.
    """
    
    return await _dispatch_email(
        to_email=email,
        subject=subject,
        html=html_content,
        text=text_content,
    )


async def send_subscription_confirmation_email(
    email: str,
    name: str,
    plan: str,
    amount: float,
    billing_cycle: str,
    next_billing_date: "datetime"
) -> bool:
    """Send subscription purchase confirmation."""
    from datetime import datetime
    
    subject = f"🎉 Welcome to {plan.title()} Plan - Subscription Activated!"
    
    next_billing_str = next_billing_date.strftime("%B %d, %Y")
    
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
    </head>
    <body style="margin: 0; padding: 20px; background-color: #F9FAFB;">
        {get_email_template_header()}
        <!-- Content -->
        <div style="padding: 40px 30px; background-color: #ffffff;">
            <h2 style="color: #111827; margin: 0 0 20px 0; font-size: 28px; text-align: center;">
                🎉 Subscription Activated!
            </h2>
            <p style="color: #4B5563; font-size: 16px; line-height: 1.6; margin: 0 0 25px 0;">
                Hi <strong>{name}</strong>,
            </p>
            <p style="color: #4B5563; font-size: 16px; line-height: 1.6; margin: 0 0 25px 0;">
                Thank you for subscribing! Your <strong>{plan.title()} Plan</strong> is now active.
                Welcome to the premium experience! 🚀
            </p>
            <!-- Payment Receipt -->
            <div style="background: linear-gradient(135deg, #10B981 0%, #059669 100%); padding: 30px; border-radius: 12px; margin: 30px 0;">
                <h3 style="color: #ffffff; margin: 0 0 20px 0; font-size: 20px; text-align: center;">
                    📄 Payment Receipt
                </h3>
                <div style="background-color: rgba(255,255,255,0.2); padding: 20px; border-radius: 8px;">
                    <table style="width: 100%; color: #ffffff;">
                        <tr>
                            <td style="padding: 10px 0; font-size: 14px;">Plan:</td>
                            <td style="padding: 10px 0; text-align: right; font-weight: bold; font-size: 14px;">{plan.title()} - {billing_cycle.title()}</td>
                        </tr>
                        <tr>
                            <td style="padding: 10px 0; font-size: 14px;">Amount Paid:</td>
                            <td style="padding: 10px 0; text-align: right; font-weight: bold; font-size: 18px;">₹{amount}</td>
                        </tr>
                        <tr>
                            <td style="padding: 10px 0; font-size: 14px;">Next Billing:</td>
                            <td style="padding: 10px 0; text-align: right; font-weight: bold; font-size: 14px;">{next_billing_str}</td>
                        </tr>
                    </table>
                </div>
            </div>
            <!-- Plan Features -->
            <div style="background-color: #F9FAFB; padding: 25px; border-radius: 8px; margin: 30px 0;">
                <h3 style="color: #111827; margin: 0 0 15px 0; font-size: 18px;">
                    ✨ Your {plan.title()} Plan Includes:
                </h3>
                <ul style="color: #4B5563; font-size: 15px; line-height: 2; margin: 0; padding-left: 20px;">
                    {"<li>📸 15 analyses per day</li>" if plan == "starter" else ""}
                    {"<li>📸 50 analyses per day</li>" if plan == "pro" else ""}
                    {"<li>📸 150 analyses per day</li>" if plan == "business" else ""}
                    <li>🎥 Video analysis support</li>
                    <li>⚡ Priority processing speed</li>
                    <li>🎨 Advanced prompt outputs</li>
                    {"<li>🔌 API access (5,000 calls/month)</li>" if plan in ["pro", "business"] else ""}
                    {"<li>🔌 API access (20,000 calls/month)</li>" if plan == "business" else ""}
                    <li>💬 Priority email support</li>
                    {"<li>👨‍💼 Dedicated account manager</li>" if plan == "business" else ""}
                </ul>
            </div>
            <!-- CTA -->
            <div style="text-align: center; margin: 40px 0;">
                <a href="https://prompt-detective.vercel.app/dashboard"
                   style="display: inline-block; background: linear-gradient(135deg, #8B5CF6 0%, #3B82F6 100%);
                          color: #ffffff; text-decoration: none; padding: 16px 40px; border-radius: 10px;
                          font-weight: bold; font-size: 16px; margin: 10px;">
                    🎯 Go to Dashboard
                </a>
            </div>
        </div>
        {get_email_template_footer()}
    </body>
    </html>
    """
    
    text_content = f"""
    Subscription Activated!

    Hi {name},

    Your {plan.title()} Plan is now active!

    Payment Receipt:
    - Plan: {plan.title()} - {billing_cycle.title()}
    - Amount Paid: ₹{amount}
    - Next Billing: {next_billing_str}

    Your plan includes:
    - Enhanced daily analyses
    - Video analysis support
    - Priority processing
    - Priority email support

    Start now: https://prompt-detective.vercel.app/dashboard

    © 2025 Prompt Detective. All rights reserved.
    """
    
    return await _dispatch_email(
        to_email=email,
        subject=subject,
        html=html_content,
        text=text_content,
    )


async def send_payment_success_email(
    email: str,
    name: str,
    amount: float,
    description: str,
    valid_until: "datetime"
) -> bool:
    """Send payment success email for credit packs."""
    from datetime import datetime
    
    subject = "💳 Payment Successful - Credit Pack Activated!"
    
    valid_until_str = valid_until.strftime("%B %d, %Y")
    
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
    </head>
    <body style="margin: 0; padding: 20px; background-color: #F9FAFB;">
        {get_email_template_header()}
        <!-- Content -->
        <div style="padding: 40px 30px; background-color: #ffffff;">
            <h2 style="color: #111827; margin: 0 0 20px 0; font-size: 28px; text-align: center;">
                💳 Payment Successful!
            </h2>
            <p style="color: #4B5563; font-size: 16px; line-height: 1.6; margin: 0 0 25px 0;">
                Hi <strong>{name}</strong>,
            </p>
            <p style="color: #4B5563; font-size: 16px; line-height: 1.6; margin: 0 0 25px 0;">
                Your payment has been successfully processed. Your credit pack is now active! 🎉
            </p>
            <!-- Payment Details -->
            <div style="background: linear-gradient(135deg, #10B981 0%, #059669 100%); padding: 30px; border-radius: 12px; margin: 30px 0;">
                <h3 style="color: #ffffff; margin: 0 0 20px 0; font-size: 20px; text-align: center;">
                    📄 Payment Receipt
                </h3>
                <div style="background-color: rgba(255,255,255,0.2); padding: 20px; border-radius: 8px;">
                    <table style="width: 100%; color: #ffffff;">
                        <tr>
                            <td style="padding: 10px 0; font-size: 14px;">Purchase:</td>
                            <td style="padding: 10px 0; text-align: right; font-weight: bold; font-size: 14px;">{description}</td>
                        </tr>
                        <tr>
                            <td style="padding: 10px 0; font-size: 14px;">Amount Paid:</td>
                            <td style="padding: 10px 0; text-align: right; font-weight: bold; font-size: 18px;">₹{amount}</td>
                        </tr>
                        <tr>
                            <td style="padding: 10px 0; font-size: 14px;">Valid Until:</td>
                            <td style="padding: 10px 0; text-align: right; font-weight: bold; font-size: 14px;">{valid_until_str}</td>
                        </tr>
                    </table>
                </div>
            </div>
            <!-- CTA -->
            <div style="text-align: center; margin: 40px 0;">
                <a href="https://prompt-detective.vercel.app/dashboard"
                   style="display: inline-block; background: linear-gradient(135deg, #8B5CF6 0%, #3B82F6 100%);
                          color: #ffffff; text-decoration: none; padding: 16px 40px; border-radius: 10px;
                          font-weight: bold; font-size: 16px; margin: 10px;">
                    🎯 Start Analyzing
                </a>
            </div>
        </div>
        {get_email_template_footer()}
    </body>
    </html>
    """
    
    text_content = f"""
    Payment Successful!

    Hi {name},

    Your payment has been successfully processed.

    Payment Receipt:
    - Purchase: {description}
    - Amount Paid: ₹{amount}
    - Valid Until: {valid_until_str}

    Start now: https://prompt-detective.vercel.app/dashboard

    © 2025 Prompt Detective. All rights reserved.
    """
    
    return await _dispatch_email(
        to_email=email,
        subject=subject,
        html=html_content,
        text=text_content,
    )