from django.conf import settings
from os import path
from django.db import IntegrityError

from . import uptomate
from . import tasks
from . import models


if settings.IN_TEST_MODE:
    uptomate.Deployment.TEST_MODE = True


def _task_dict_success(task):
    return {
        'task_id': task.id
    }, 200


def _vagr_factory(vm_slug, vagrant_name=None, provider=None, file_locs=None):
    """
    Uptomate vagrant factory method
    :param vm_slug: Slug to be used in the fs
    :param vagrant_name: File name of Vagrantfile to link to
    :param provider: Either name of a legit provider or a provider object
    :param file_locs: Location of the files to copy to deployment folder
    """
    if file_locs is None:
        file_locs = []
    if not file_locs:
        file_locs = [
            path.join(
                settings.DEPLOYMENT_SRC_BASEDIR,
                vm_slug,
                def_file_name) for def_file_name in uptomate.Deployment.DEFAULT_FILE_NAMES
        ]

    if isinstance(provider, str):
        try:
            provider = uptomate.Provider.ALLOWED_PROVIDERS[provider]
        except KeyError:
            raise ValueError("Provider {} not known".format(provider))

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

    t = tasks.create_deployment.delay(vagr)
    vm.add_task(t)

    return _task_dict_success(t)


def destroy_deployment(vm):
    vagr = _vagr_factory(vm.slug)
    return _task_dict_success(tasks.destroy_deployment.delay(vagr, vm))


def destroy_deployment_db(vm):
    tasks.destroy_vm_db(vm)
    return "Deleted from db", 200


def destroy_deployment_fs(vm_slug):
    return _task_dict_success(_async_res_from_slug(tasks.destroy_vm_fs, vm_slug))


def _async_res_from_slug(task, vm_slug, **kwargs):
    vagr = _vagr_factory(vm_slug, **kwargs)
    return task.delay(vagr)


def run_on_existing(task, vm_obj, **kwargs):
    t = _async_res_from_slug(task, vm_obj.slug, **kwargs)
    vm_obj.add_task(t)
    return _task_dict_success(t)
