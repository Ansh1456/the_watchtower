from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings

@shared_task
def send_otp_email_task(email, otp):
    """
    Sends the OTP email asynchronously so it doesn't block the web thread.
    """
    try:
        user_email = getattr(settings, 'EMAIL_HOST_USER', None)
        
        # If in local dev environment and no email configured, skip blocking SMTP call
        if not user_email:
            print(f"\n[DEV MODE] Skipping actual email send. OTP code for {email} is: {otp}\n")
            return True

        send_mail(
            "The Watchtower Verification",
            f"Your OTP code is {otp}",
            user_email,
            [email],
            fail_silently=True,
        )
        return True
    except Exception as e:
        print(f"SMTP error ignored: {e}")
        return False
