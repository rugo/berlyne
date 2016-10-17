from django.shortcuts import get_object_or_404
from django.core.exceptions import ObjectDoesNotExist
from . import models
from . import util
from . import deploy_controller


def vm_start(request, vm_slug, provider=None):
    vm = get_object_or_404(models.VirtualMachine, slug=vm_slug)
    return util.http_json_response(
        *deploy_controller.start_deployment(vm, provider)
    )


def vm_status(request, vm_slug):
    vm = get_object_or_404(models.VirtualMachine, slug=vm_slug)

    try:
        task_list = [t.to_dict() for t in vm.task_set.all().order_by('-creation_date')]
    except ObjectDoesNotExist:
        task_list = None

    return util.http_json_response(
            {
                'slug': vm_slug,
                'task_info': task_list if task_list else "None"
            }
    )


def vm_create(request, vm_slug, vagrant_name):
    return util.http_json_response(
        *deploy_controller.create_deployment(vm_slug, vagrant_name)
    )
