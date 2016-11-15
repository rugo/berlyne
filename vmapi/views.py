from django.shortcuts import get_object_or_404
from django.core.exceptions import ObjectDoesNotExist
from . import models
from . import util
from . import deploy_controller
from django.contrib.auth.decorators import permission_required


def _run_task_on_existing_vm(action, vm_slug, **kwargs):
    vm = get_object_or_404(models.VirtualMachine, slug=vm_slug)
    return util.http_json_response(
        *deploy_controller.run_on_existing(action, vm, **kwargs)
    )

@permission_required('can_manage_vm')
def vm_start_provider(request, vm_slug, provider):
    return _run_task_on_existing_vm('start', vm_slug, provider=provider)


@permission_required('can_manage_vm')
def vm_action(request, vm_slug, action_name):
    return _run_task_on_existing_vm(action_name, vm_slug)


@permission_required('can_manage_vm')
def vm_destroy(request, vm_slug):
    vm = get_object_or_404(models.VirtualMachine, slug=vm_slug)
    return util.http_json_response(
        *deploy_controller.destroy_deployment(vm)
    )


@permission_required('can_manage_vm')
def vm_destroy_fs(request, vm_slug):
    return util.http_json_response(
        *deploy_controller.destroy_deployment_fs(vm_slug)
    )


@permission_required('can_manage_vm')
def vm_destroy_db(request, vm_slug):
    vm = get_object_or_404(models.VirtualMachine, slug=vm_slug)
    return util.http_json_response(
        *deploy_controller.destroy_deployment_db(vm)
    )


@permission_required('can_manage_vm')
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


@permission_required('can_manage_vm')
def vm_create(request, vm_slug, vagrant_name):
    return util.http_json_response(
        *deploy_controller.create_deployment(vm_slug, vagrant_name)
    )


@permission_required('can_manage_vm')
def task_state(request, task_id):
    task = get_object_or_404(models.Task, task_id=task_id)
    res = task.to_dict()

    return util.http_json_response(
        res, 200
    )
