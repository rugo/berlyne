from django.conf import settings
from os import path

from . import uptomate
from . import tasks
from . import models

# TODO: remove
uptomate.Deployment.TEST_MODE = True

def _vagr_factory(vm_slug, vagrant_name, file_locs=[]):
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
        deployment_path=settings.VAGR_DEPLOYMENT_PATH,
        vagrant_path=settings.VAGR_VAGRANT_PATH,
        file_locs=file_locs
    )


def create_deployment(vm_slug, vagrant_name):
    vagr = _vagr_factory(vm_slug, vagrant_name)
    if vagr.exists:
        return "VM with that name already exists", 419
    # task create
    vm = models.VirtualMachine(slug=vm_slug)
    task = tasks.create_deployment.delay(vagr)
    vm.save()
    vm.task_set.create(task_meta_id=task.id)

    return "Created deployment job", 200
