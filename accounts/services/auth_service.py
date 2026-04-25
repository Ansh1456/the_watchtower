import random
import logging
from accounts.tasks import send_otp_email_task

logger = logging.getLogger(__name__)

def generate_and_send_otp(email):
    otp = random.randint(100000, 999999)
    try:
        # Try to offload the blocking SMTP call to Celery/Redis asynchronously
        send_otp_email_task.delay(email, otp)
    except Exception as e:
        logger.warning(f"Celery task failed (Redis probably offline: {e}). Falling back to sync execution.")
        # Fallback: Execute it synchronously right now
        send_otp_email_task(email, otp)
    
    return otp
