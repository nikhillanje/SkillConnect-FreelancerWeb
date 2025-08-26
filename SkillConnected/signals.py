from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import FreelancerLogin, ClientLogin
from .utils import send_account_approval_email

@receiver(post_save, sender=FreelancerLogin)
def send_freelancer_approval_email(sender, instance, created, **kwargs):
    if not created:  # only on update
        if instance.is_approved:  # if approved
            send_account_approval_email(instance.email, instance.first_name)




@receiver(post_save, sender=ClientLogin)
def send_client_approval_email(sender, instance, created, **kwargs):
    if not created:  # only on update
        if instance.is_approved:  # if approved
            send_account_approval_email(instance.email, instance.first_name)

            