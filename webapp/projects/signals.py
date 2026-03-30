from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Project


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_default_project(sender, instance, created, **kwargs):
    if created:
        name = instance.company_name or 'My Project'
        Project.objects.create(owner=instance, name=name)
