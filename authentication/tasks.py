import dramatiq
from .email_services import EmailService, PasswordResetEmailStrategy

@dramatiq.actor
def send_password_reset_email_async(recipient_email, reset_link):
    email_service = EmailService()
    strategy = PasswordResetEmailStrategy()
    email_service.send_email(
        recipient_email=recipient_email,
        strategy=strategy,
        reset_link=reset_link
    )