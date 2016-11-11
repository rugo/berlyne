from django.db.models.signals import post_migrate
from django.dispatch import receiver
from django.contrib.auth.models import Group, Permission, User
from django.contrib.contenttypes.models import ContentType
from . import models
from vmapi import models as api_models
from django.apps import apps
from django.contrib.flatpages.models import FlatPage
from django.contrib.sites.models import Site
from django.conf import settings
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


def __create_test_data():
    u = User.objects.create_user(
        "hans",
        "hans@hans.hans",
        "wtf123wtf"
    )

    su = User.objects.get(pk=1)
    su.groups.add(Group.objects.get(name="teachers"))

    problems = [
        api_models.VirtualMachine.objects.create(
            slug="WebTask",
            ip_addr="127.0.0.1",
            desc="A web task",
            category="Web",
            flag="flag{hoho}"
        ),
        api_models.VirtualMachine.objects.create(
            slug="PwnTask",
            ip_addr="127.0.0.1",
            desc="A pwn task",
            category="Pwn",
            flag="flag{hoho}"
        )
    ]

    course = models.Course.objects.create(
        name="Pwnable",
        description="A test course",
        show_scoreboard=True,
        teacher=su,
        point_threshold=300,
        writeups=True
    )

    course.participants.add(u, su)

    for problem in problems:
        models.CourseProblems.objects.create(
            course=course,
            problem=problem,
            points=150
        )





@receiver(post_migrate, sender=apps.get_app_config('wui'))
def init_groups(sender, **kwargs):
    logger.info("Running post_migrate routine for 'wui'")
    __setup_create_groups()
    __setup_frontpage()
    if settings.IN_TEST_MODE:
        __create_test_data()