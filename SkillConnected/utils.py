from django.core.mail import send_mail
from django.conf import settings

def send_account_approval_email(email, name):
    subject = "SkillConnect Account Approved"
    message = f"Hello {name},\n\nYour SkillConnect Account has been approved. Now you can log in and access your account.\n\nThank you,\nSkillConnect Team"
    from_email = settings.EMAIL_HOST_USER
    recipient_list = [email]

    send_mail(subject, message, from_email, recipient_list)