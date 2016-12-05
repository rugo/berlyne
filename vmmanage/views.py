from django.shortcuts import get_object_or_404, render, redirect
from django.core.exceptions import ObjectDoesNotExist
from django.conf import settings
from django.http import HttpResponseNotAllowed
from . import models
from . import util
from . import deploy_controller
from . import forms
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.decorators import permission_required
from django.urls import reverse


_INSTALL_MSGS = {
    'formerror': _("The submitted form was invalid!"),
    'success': _("The problem is getting installed, this may take a while."),
    'exists': _("A problem with that slug is already installed!")
}


def _run_task_on_existing_vm(action, vm_slug, **kwargs):
    vm = get_object_or_404(models.VirtualMachine, slug=vm_slug)
    return util.http_json_response(
        *deploy_controller.run_on_existing(action, vm, **kwargs)
    )


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
        res, deploy_controller.HTTP_OK
    )


# TODO: Make nicer, enhance usability in case of F-5s and get param
@permission_required("can_manage_vm")
def show_installable_problems(request):
    problems = deploy_controller.find_installable_problems()
    msgs = []
    if not problems:
        msgs.append(_("No problems are available for installation"))

    _msg = request.GET.get("m", "")
    if _msg:
        msgs.append(_INSTALL_MSGS[_msg])

    return render(
        request,
        "vms/installable.html",
        {
            "problems": problems,
            "vagrant_form": forms.VagrantFilesForm(
                initial={'vagrant_file': settings.VAGR_DEFAULT_VAGR_FILE}
            ),
            "errors": msgs,
        }
    )


@permission_required("can_manage_vm")
def problem_destroy(request, problem_slug):
    problem = get_object_or_404(models.VirtualMachine, slug=problem_slug)
    if request.POST:
        deploy_controller.destroy_deployment(problem)
        return redirect('vmmanage_show_problems')
    return render(
        request,
        "vms/destroy_submission.html",
        {
            "problem": problem,
        }
    )


@permission_required("can_manage_vm")
def install_problem(request):
    if not request.POST:
        return redirect('vmmanage_show_installable')
    form = forms.VagrantFilesForm(request.POST)
    if form.is_valid():
        vagr_name = form.cleaned_data['vagrant_file']
        problem_name = request.POST['problem']
        reason, code = deploy_controller.create_deployment(problem_name, vagr_name)
        if code == deploy_controller.HTTP_CONFLICT:
            return redirect(reverse('vmmanage_show_installable') + '?m=exists')
    else:
        return redirect(reverse('vmmanage_show_installable') + '?m=formerror')

    return redirect(
        reverse('vmmanage_show_installable') + '?m=success'
    )

@permission_required("can_manage_vm")
def problem_overview(request):
    return render(
        request,
        "vms/overview.html",
        {
            "problems": models.VirtualMachine.objects.all(),
        }
    )


@permission_required("can_manage_vm")
def perform_action(request, problem_slug, action_name):
    res = _run_task_on_existing_vm(action_name, problem_slug)
    if res.status_code != deploy_controller.HTTP_OK:
        return HttpResponseNotAllowed(res.content)
    return redirect(
        'vmmanage_detail_problem',
        problem_slug=problem_slug
    )


@permission_required("can_manage_vm")
def problem_detail(request, problem_slug):
    return render(
        request,
        "vms/detail.html",
        {
            "problem": get_object_or_404(models.VirtualMachine,
                                         slug=problem_slug),
            "actions": deploy_controller.LEGAL_API_VM_ACTIONS
        }
    )


@permission_required("can_manage_vm")
def edit_problem(request, problem_slug):
    problem = get_object_or_404(models.VirtualMachine, slug=problem_slug)

    if request.POST:
        form = forms.ProblemEditForm(request.POST,
                                     instance=problem)
        if form.is_valid():
            form.save()
    else:
        form = forms.ProblemEditForm(instance=problem)

    return render(
        request,
        "vms/edit.html",
        {
            "problem": problem,
            "form": form
        }
    )
