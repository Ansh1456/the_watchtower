import random
import logging
from accounts.tasks import send_otp_email_task

logger = logging.getLogger(__name__)

def generate_and_send_otp(email):
    otp = random.randint(100000, 999999)

    # Send synchronously — no daemon thread.
    # A daemon thread on Gunicorn gets killed before it finishes, which is
    # exactly why emails were silently never delivered on Render.
    # The 1-2s SMTP delay on registration is acceptable.
    try:
        send_otp_email_task(email, otp)
    except Exception as exc:
        # SMTP failed but OTP is still stored in session and printed to logs.
        # Registration can continue; user can use "Resend code" if needed.
        logger.error(f"[OTP] Email delivery failed for {email}: {exc}")

    return otp
