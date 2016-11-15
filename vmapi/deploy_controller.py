from django.conf import settings
from os import path
from django.db import IntegrityError

from .uptomate.Deployment import Vagrant
from .uptomate import Deployment, Provider
from . import tasks
from . import models


LEGAL_API_VM_ACTIONS = [
    'start',
    'stop',
    'status',
    'address',
    'resume',
    'suspend',
    'reload'
]


def _task_dict_success(task):
    return {
        'task_id': task.pk
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
                def_file_name) for def_file_name in Deployment.DEFAULT_FILE_NAMES
        ]

    if isinstance(provider, str):
        try:
            provider = Provider.ALLOWED_PROVIDERS[provider]
        except KeyError:
            raise ValueError("Provider {} not known".format(provider))

    return Vagrant(
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

    t = tasks.run_on_vagr(
        vagr,
        'create'
    )
    vm.add_task(t)

    return _task_dict_success(t)


def destroy_deployment(vm):
    vagr = _vagr_factory(vm.slug)
    return _task_dict_success(tasks.destroy_deployment(vagr, vm))


def destroy_deployment_db(vm):
    tasks.destroy_vm_db(vm)
    return "Deleted from db", 200


def destroy_deployment_fs(vm_slug):
    return _task_dict_success(_task_from_slug(
        'destroy',
        vm_slug)
    )


def _task_from_slug(action, vm_slug, vm_db=None, **kwargs):
    vagr = _vagr_factory(vm_slug, **kwargs)
    return tasks.run_on_vagr(vagr, action, vm_db)


def run_on_existing(action, vm_obj, **kwargs):
    if action not in LEGAL_API_VM_ACTIONS:
        return "Action is not defined", 404
    t = _task_from_slug(action, vm_obj.slug, vm_obj, **kwargs)
    vm_obj.add_task(t)
    return _task_dict_success(t)
