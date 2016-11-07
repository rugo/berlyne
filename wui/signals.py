from django.db.models.signals import post_migrate
from django.dispatch import receiver
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from . import models
from django.contrib.flatpages.models import FlatPage
from django.contrib.sites.models import Site
import logging

logger = logging.getLogger(__name__)


def __setup_create_groups():
    group, created = Group.objects.get_or_create(name='teachers')
    perm = Permission.objects.create(
        codename="can_manage_course",
        name="can manage course",
        content_type=ContentType.objects.get_for_model(models.Course))
    if created:
        group.permissions.add(perm)


def __setup_frontpage():
    fp, _ = FlatPage.objects.get_or_create(url="/",
                                 title="welcome",
                                 content="<h1>Welcome</h1>")
    s = Site.objects.first()
    s.domain = "berlyne.tld"
    s.name = "Berlyne.tld"
    s.save()
    fp.sites.add(s)


# TODO: Change to specific sender
@receiver(post_migrate)
def init_groups(sender, **kwargs):
    if sender.name != 'wui':
        return
    logger.info("Running post_migrate routine for 'wui'")
    __setup_create_groups()
    __setup_frontpage()