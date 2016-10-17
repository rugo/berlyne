from django.conf import settings
from os import path
from django.db import IntegrityError

from . import uptomate
from . import tasks
from . import models

# TODO: remove
uptomate.Deployment.TEST_MODE = True


def _vagr_factory(vm_slug, vagrant_name=None, provider=None, file_locs=[]):
    if not file_locs:
        file_locs = [
            path.join(
                settings.DEPLOYMENT_SRC_BASEDIR,
                vm_slug,
                def_file_name) for def_file_name in uptomate.Deployment.DEFAULT_FILE_NAMES
        ]
    return uptomate.Deployment.Vagrant(
        vm_slug,
        vagrant_name=vagrant_name,
        provider=provider,
        deployment_path=settings.VAGR_DEPLOYMENT_PATH,
        vagrant_path=settings.VAGR_VAGRANT_PATH,
        file_locs=file_locs
    )

def create_deployment(vm_slug, vagrant_name):
    if isinstance(vm_slug, models.VirtualMachine):
        vm_slug = vm_slug.slug

    vagr = _vagr_factory(vm_slug, vagrant_name)
    if vagr.exists:
        return "VM with that name already exists in fs", 419

    try:
        vm = models.VirtualMachine.objects.create(slug=vm_slug)
    except IntegrityError:
        return "VM exists already in db", 419

    vm.add_task(tasks.create_deployment.delay(vagr))

    return "Created deployment job", 200

def start_deployment(vm_obj, provider):
    vagr = _vagr_factory(vm_obj.slug, provider=provider)
    if not vagr.exists:
        return "VM with this name does not exist", 404
    vm_obj.add_task(tasks.start_deployment.delay(vagr))
    return "Created start job", 200

