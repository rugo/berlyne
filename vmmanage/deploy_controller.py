from django.conf import settings
from os import path
from django.db import IntegrityError
from glob import glob
from http.client import (
    OK as HTTP_OK,
    CONFLICT as HTTP_CONFLICT
)

from uptomate.Deployment import (
    Vagrant,
    INSTANCE_DIR_NAME,
    INSTALLED_MARKER_FILE
)
from uptomate import Deployment, Provider
from . import tasks
from . import models


LEGAL_API_VM_ACTIONS = [
    'start',
    'stop',
    'status',
    # 'address',
    'resume',
    'suspend',
    'reload'
]

FLAG_FILE_NAME = "flag.txt"


__AVAIL_VAGR_FILES = []


def get_avail_vagrant_files():
    if not __AVAIL_VAGR_FILES:
        for p in glob(path.join(settings.VAGR_VAGRANT_PATH, '*')):
            if path.isfile(p):
                __AVAIL_VAGR_FILES.append(path.split(p)[-1])
    return __AVAIL_VAGR_FILES


def _task_dict_success(task):
    return {
        'task_id': task.pk
    }, HTTP_OK


def _vagr_factory(vm_slug):
    return Vagrant(
        vm_slug,
        deployment_path=settings.VAGR_DEPLOYMENT_PATH,
    )


def install_deployment(vagr_depl: Deployment.Vagrant, vm):
    if isinstance(vm, str):
        vm = models.VirtualMachine.objects.get(slug=vm)

    try:
        config = vm.set_align_config(vagr_depl.get_config())
    except KeyError as ex:
        raise ValueError("Problem config is missing '{}' field".format(str(ex)))

    vagr_depl.set_ports(config['ports'])

    with vagr_depl.open_content_file(FLAG_FILE_NAME) as f:
        f.write(config['flag'])


def __install_deployment_callback(vagr_depl, f, vm_db, **kwargs):
    install_deployment(vagr_depl, vm_db)


def create_deployment(vm_slug, vagrant_name):

    if isinstance(vm_slug, models.VirtualMachine):
        vm_slug = vm_slug.slug

    vagr = _vagr_factory(vm_slug)
    if vagr.installed:
        return "VM with that name already exists in fs", HTTP_CONFLICT

    try:
        vm = models.VirtualMachine.objects.create(slug=vm_slug)
    except IntegrityError:
        return "VM exists already in db", HTTP_CONFLICT

    t = tasks.run_on_vagr(
        vagr,
        'create',
        vm,
        __install_deployment_callback,
        vagrant_file_path=path.join(settings.VAGR_VAGRANT_PATH, vagrant_name)
    )

    vm.add_task(t, 'create')
    return _task_dict_success(t)


def destroy_deployment(vm):
    vagr = _vagr_factory(vm.slug)
    return _task_dict_success(tasks.destroy_deployment(vagr, vm))


def destroy_deployment_db(vm):
    tasks.destroy_vm_db(vm)
    return "Deleted from db", HTTP_OK


def destroy_deployment_fs(vm_slug):
    return _task_dict_success(_task_from_slug(
        'destroy',
        vm_slug)
    )


def _task_from_slug(action, vm_slug, vm_db=None, **kwargs):
    vagr = _vagr_factory(vm_slug)
    return tasks.run_on_vagr(vagr, action, vm_db, **kwargs)


def run_on_existing(action, vm_obj, **kwargs):
    if action not in LEGAL_API_VM_ACTIONS:
        return "Action is not defined", 404
    t = _task_from_slug(action, vm_obj.slug, vm_obj, **kwargs)
    vm_obj.add_task(t, action)
    return _task_dict_success(t)


def find_installable_problems():
    problems = []
    for task_path in glob(
            path.join(
                settings.VAGR_DEPLOYMENT_PATH,
                "*",
                Deployment.CONFIG_FILE_NAME
            )
    ):
        if not path.exists(
                path.join(task_path, INSTANCE_DIR_NAME, INSTALLED_MARKER_FILE)
        ):
            problems.append(path.split(path.dirname(task_path))[-1])
    return problems
