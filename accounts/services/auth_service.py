import random
import logging
import threading
from accounts.tasks import send_otp_email_task

logger = logging.getLogger(__name__)

def generate_and_send_otp(email):
    otp = random.randint(100000, 999999)
    
    # Use threading to run the email sending in the background
    # This avoids issues with Celery workers dying on free tier deployments
    # but still prevents blocking the main request thread.
    try:
        thread = threading.Thread(target=send_otp_email_task, args=(email, otp))
        thread.daemon = True
        thread.start()
    except Exception as e:
        logger.error(f"Failed to start thread for OTP email: {e}")
        # Ultimate fallback
        send_otp_email_task(email, otp)
        
    return otp
