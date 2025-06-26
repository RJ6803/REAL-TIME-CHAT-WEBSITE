from django.dispatch import receiver
from django.db.models.signals import post_save,pre_save
from allauth.account.models import EmailAddress
from allauth.account.utils import get_user_model
from django.contrib.auth.models import User
from .models import Profile

@receiver(post_save, sender=User)
def user_postsave(sender, instance, created, **kwargs):
    user = instance

    if created and not hasattr(user, 'profile'):
        Profile.objects.create(user=user)

    else:
        email_address = EmailAddress.objects.filter(user=user, primary=True).first()


        if email_address:
            # If a primary email exists, check if it matches the user's email
            if email_address.email != user.email:
                email_address.email = user.email
                email_address.verified = False
                email_address.save()
        else:
            # No primary email — check if email already exists to avoid unique constraint error
            existing = EmailAddress.objects.filter(user=user, email=user.email).first()
            if not existing:
                EmailAddress.objects.create(
                    user=user,
                    email=user.email,
                    primary=True,
                    verified=False
                )

@receiver(pre_save,sender=User)
def user_persave(sender,instance,**kwargs):
    if instance.username:
        instance.username=instance.username.lower()

