from django.contrib.auth.models import Group, Permission, User
from django.contrib.contenttypes.models import ContentType
from . import models
from os.path import join as _joinp
from vmmanage import models as api_models
from vmmanage import deploy_controller, tasks, models as vm_models
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
        "participant",
        "hans@hans.hans",
        "NoGood123"
    )

    su = User.objects.create_user(
        "admin",
        "not@lol.tld",
        "NoGood123",
        is_staff=True,
        is_superuser=True
    )

    tut_slug = "tutorial"
    su.groups.add(Group.objects.get(name="teachers"))

    problem = api_models.VirtualMachine.objects.create(
            slug=tut_slug,
            name="Tutorial"
    )

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


    models.CourseProblems.objects.create(
            course=course,
            problem=problem,
            points=150
    )

    tasks.run_on_vagr(
        vm_models.vagr_factory(tut_slug),
        "install",
        problem,
        deploy_controller._install_deployment_callback,
        vagrant_file_path=_joinp(settings.VAGR_VAGRANT_PATH,
                                 settings.VAGR_DEFAULT_VAGR_FILE)
    )


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
