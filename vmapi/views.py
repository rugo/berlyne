from django.shortcuts import get_object_or_404
from django.core.exceptions import ObjectDoesNotExist
from . import models
from . import util
from . import deploy_controller
from . import tasks
from celery import current_app


def vm_start(request, vm_slug, provider=None):
    vm = get_object_or_404(models.VirtualMachine, slug=vm_slug)
    return util.http_json_response(
        *deploy_controller.run_on_existing(tasks.start_deployment, vm, provider=provider)
    )


def vm_stop(request, vm_slug):
    vm = get_object_or_404(models.VirtualMachine, slug=vm_slug)
    return util.http_json_response(
        *deploy_controller.run_on_existing(tasks.stop_deployment, vm)
    )


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


def vm_status(request, vm_slug):
    vm = get_object_or_404(models.VirtualMachine, slug=vm_slug)
    return util.http_json_response(
        *deploy_controller.run_on_existing(tasks.status_of_deployment, vm)
    )


def task_state(request, task_id):
    task = get_object_or_404(models.Task, task_id=task_id)
    return util.http_json_response(
        task.to_dict(), 200
    )