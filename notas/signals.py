from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import Profile, Plan

@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    if created:
        default_plan = Plan.objects.filter(role="member").first()
        Profile.objects.create(
            user=instance,
            role="member",
            plan=default_plan
        )
