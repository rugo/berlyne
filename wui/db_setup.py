from django.contrib.auth.models import Group, Permission, User
from django.contrib.contenttypes.models import ContentType
from . import models
from os.path import join as _joinp
from vmmanage import models as api_models
from vmmanage import deploy_controller
from django.contrib.flatpages.models import FlatPage
from django.contrib.sites.models import Site
from django.conf import settings
from django.utils import timezone
from django.db import IntegrityError
import logging

logger = logging.getLogger(__name__)


def __setup_create_groups():
    group, created = Group.objects.get_or_create(name='teachers')
    perm_course = Permission.objects.create(
        codename="can_manage_course",
        name="can manage course",
        content_type=ContentType.objects.get_for_model(models.Course))
    perm_vm = Permission.objects.create(
        codename="can_manage_vm",
        name="can manage vm",
        content_type=ContentType.objects.get_for_model(models.Course))
    if created:
        group.permissions.add(perm_course, perm_vm)


def __setup_frontpage():
    init_content = open(
        _joinp(settings.BASE_DIR, "res", "init_data", "welcome_init.html")
    ).read()
    fp, _ = FlatPage.objects.get_or_create(
        url="/",
        title="welcome",
        content=init_content
    )
    s = Site.objects.first()
    s.domain = settings.ALLOWED_HOSTS[0]
    s.name = "Berlyne"
    s.save()
    fp.sites.add(s)


def __create_test_data():
    u = User.objects.create_user(
        "hans",
        "hans@hans.hans",
        "wtf123wtf"
    )

    su = User.objects.create_user(
        "rg",
        "not@lol.tld",
        "penis123",
        is_staff=True,
        is_superuser=True
    )

    su.groups.add(Group.objects.get(name="teachers"))

    problems = [
        api_models.VirtualMachine.objects.create(
            slug="WebTask",
            name="Super Web Task",
            ip_addr="127.0.0.1",
            desc="A web task",
            category="Web",
            flag="flag{hoho}",
            default_points=100
        ),
        api_models.VirtualMachine.objects.create(
            slug="PwnTask",
            name="Hard PWN Task",
            ip_addr="127.0.0.1",
            desc="A pwn task",
            category="Pwn",
            flag="flag{hoho}",
            default_points=200
        )
    ]

    course = models.Course.objects.create(
        name="Pwnable",
        description="A test course",
        show_scoreboard=True,
        teacher=su,
        point_threshold=300,
        writeups=True,
        start_time=timezone.now(),
        deadline=timezone.now() + timezone.timedelta(weeks=1)
    )

    course.participants.add(u, su)

    for problem in problems:
        models.CourseProblems.objects.create(
            course=course,
            problem=problem,
            points=150
        )
        problem.state_set.add(api_models.State(name="Installed"), bulk=False)

    txt, res = deploy_controller.create_deployment("tutorial", "ubuntu_docker")
    if res != 200:
        log("Could not create deployment: " + txt)


def log(msg, level=logging.WARN):
    logger.log(level, "[Berlyne] " + msg)


def setup():
    """
    Creates initial data
    """
    log("Creating inital berlyne data")
    try:
        __setup_create_groups()
        __setup_frontpage()
    except IntegrityError:
        log("Could not initialize db! Is the db already initialized?")
    if settings.IN_TEST_MODE:
        log("creating test data since IN_TEST_MODE is true")
        __create_test_data()
