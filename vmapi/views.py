from django.shortcuts import get_object_or_404

from django.core.exceptions import ObjectDoesNotExist
from . import models
from . import util
from . import deploy_controller


def vm_status(request, vm_slug):
    vm = get_object_or_404(models.VirtualMachine, slug=vm_slug)

    try:
        task = vm.task_set.latest('creation_date')
        task_dict = task.to_dict()
    except ObjectDoesNotExist:
        task_dict = None

    return util.http_json_response(
            {
                'slug': vm_slug,
                'last_task_info': task_dict if task_dict else "None"
            }
    )


def vm_create(request, vm_slug, vagrant_name):
    message, status = deploy_controller.create_deployment(vm_slug, vagrant_name)
    return util.http_json_response(message, status)
