from django.core.mail import send_mail, EmailMultiAlternatives
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

# Keep @shared_task signature so existing imports don't break,
# but the function is now also called synchronously from auth_service.
try:
    from celery import shared_task
    _shared_task = shared_task
except ImportError:
    def _shared_task(fn):
        return fn

@_shared_task
def send_otp_email_task(email, otp):
    """
    Sends the OTP verification email.
    Always logs OTP to server console as a fallback.
    Raises on SMTP failure so the caller knows it failed.
    """
    # Always print to logs — visible in Render log tail even if email fails
    logger.info(f"[OTP] Sending code {otp} to {email}")
    print(f"\n[WATCHTOWER OTP] Code for {email} is: {otp}\n", flush=True)

    user_email = getattr(settings, 'EMAIL_HOST_USER', None)
    user_password = getattr(settings, 'EMAIL_HOST_PASSWORD', None)

    if not user_email or not user_password:
        # Credentials not configured — OTP is visible in Render logs above.
        # Log a clear warning so the operator knows what's missing.
        logger.warning(
            "[OTP] EMAIL_HOST_USER or EMAIL_HOST_PASSWORD not set. "
            "Email NOT sent. OTP is only available in server logs."
        )
        return True  # Don't crash registration — OTP is still in the session

    try:
        subject = "Your Watchtower Verification Code"
        plain_body = f"Your one-time verification code is: {otp}\n\nThis code expires after you use it."
        html_body = f"""
        <div style="font-family:Arial,sans-serif;max-width:480px;margin:auto;padding:32px;background:#0f172a;border-radius:12px;color:#e2e8f0;">
          <h2 style="color:#38bdf8;margin-bottom:8px;">The Watchtower</h2>
          <p style="color:#94a3b8;margin-bottom:24px;">System Monitoring Dashboard</p>
          <p>Your verification code is:</p>
          <div style="font-size:36px;font-weight:bold;letter-spacing:8px;color:#ffffff;background:#1e293b;padding:16px 24px;border-radius:8px;text-align:center;margin:16px 0;">{otp}</div>
          <p style="color:#64748b;font-size:13px;">Enter this code on the verification page to complete your registration. Do not share this code with anyone.</p>
        </div>
        """
        msg = EmailMultiAlternatives(subject, plain_body, user_email, [email])
        msg.attach_alternative(html_body, "text/html")
        msg.send(fail_silently=False)  # Raise on error so it's visible in logs
        logger.info(f"[OTP] Email sent successfully to {email}")
        return True
    except Exception as exc:
        logger.error(f"[OTP] SMTP send failed for {email}: {exc}", exc_info=True)
        # Re-raise so the caller can decide what to do
        raise
