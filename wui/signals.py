from django.db.models.signals import post_migrate
from django.dispatch import receiver
from django.apps import apps
from . import db_setup


@receiver(post_migrate, sender=apps.get_app_config('wui'))
def init_groups(sender, **kwargs):
    db_setup.setup()
