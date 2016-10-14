from django.shortcuts import get_object_or_404

import json
from . import models
from . import util
from . import deploy_controller

def vm_status(request, vm_slug):
    vm = get_object_or_404(models.VirtualMachine, slug=vm_slug)
    task = vm.task_set.first()
    return util.http_json_response(
            {
                'slug': vm_slug,
                'status': task.task_meta.status,
                'status_text': task.task_meta.status,
                'status_updated': 12344
            }
    )


def vm_create(request, vm_slug, vagrant_name):
    message, status = deploy_controller.create_deployment(vm_slug, vagrant_name)
    return util.http_json_response(message, status)
