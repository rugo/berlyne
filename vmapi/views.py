from django.shortcuts import get_object_or_404
from django.core.exceptions import ObjectDoesNotExist
from . import models
from . import util
from . import deploy_controller
from . import tasks


def _run_task_on_existing_vm(task, vm_slug, **kwargs):
    vm = get_object_or_404(models.VirtualMachine, slug=vm_slug)
    return util.http_json_response(
        *deploy_controller.run_on_existing(task, vm, **kwargs)
    )


def vm_start(request, vm_slug, provider=None):
    return _run_task_on_existing_vm(tasks.start_deployment, vm_slug, provider=provider)


def vm_stop(request, vm_slug):
    return _run_task_on_existing_vm(tasks.stop_deployment, vm_slug)


def vm_address(request, vm_slug):
    return _run_task_on_existing_vm(tasks.service_network_address, vm_slug)


def vm_status(request, vm_slug):
    return _run_task_on_existing_vm(tasks.status_of_deployment, vm_slug)


def vm_destroy(request, vm_slug):
    vm = get_object_or_404(models.VirtualMachine, slug=vm_slug)
    return util.http_json_response(
        *deploy_controller.destroy_deployment(vm)
    )


def vm_destroy_fs(request, vm_slug):
    return util.http_json_response(
        *deploy_controller.destroy_deployment_fs(vm_slug)
    )


def vm_destroy_db(request, vm_slug):
    vm = get_object_or_404(models.VirtualMachine, slug=vm_slug)
    return util.http_json_response(
        *deploy_controller.destroy_deployment_db(vm)
    )


def vm_tasks(request, vm_slug):
    vm = get_object_or_404(models.VirtualMachine, slug=vm_slug)

    try:
        task_list = [t.to_dict() for t in vm.task_set.all().order_by('-creation_date')]
    except ObjectDoesNotExist:
        task_list = []

    return util.http_json_response(
            {
                'tasks': task_list
            }
    )


def vm_create(request, vm_slug, vagrant_name):
    return util.http_json_response(
        *deploy_controller.create_deployment(vm_slug, vagrant_name)
    )


def task_state(request, task_id):
    try:
        task = models.Task.objects.get(task_id=task_id)
        res = task.to_dict()
    except ObjectDoesNotExist:
        res = models.Task.get_nondb_task(task_id)

    return util.http_json_response(
        res, 200
    )
