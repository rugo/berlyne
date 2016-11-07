from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, permission_required
from . import models
from django.utils.translation import ugettext_lazy as _
from django.urls import reverse
from .forms import *

MESSAGES = {
    '': None,
    'joined': _("You joined the course"),
    'deleted': _("You deleted the course"),
    'left': _("You left the course"),
    'join_first': _("Join the course first")
}


@login_required()
def profile(request):
    if request.POST:
        form = UserForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
    else:
        form = UserForm(instance=request.user)

    return render(request, 'accounts/profile.html', {'form': form})


# TODO: split course_edit
@permission_required('can_manage_course')
def course_edit(request, course_slug=None):
    if request.POST:
        form = CourseForm(request.POST)
        if course_slug:
            form.instance = get_object_or_404(models.Course, name=course_slug)
        if form.is_valid():
            form.instance.teacher = request.user
            form.save()
        if not course_slug:
            return redirect(
                reverse('wui_course_manage_problems',
                        kwargs={'course_slug': form.cleaned_data['name']})
            )
    else:
        if course_slug:
            form = CourseForm(
                instance=get_object_or_404(models.Course, name=course_slug)
            )
        else:
            form = CourseForm()
    return render(request, 'generic/model_form.html', {'headline': _('Course'),
                                                       'form': form})


# TODO: make in one query
@login_required()
def courses(request):
    return render(request, 'courses/list.html', {
        'headline': _('Courses'),
        'courses': models.Course.objects.all(),
        'message': MESSAGES.get(request.GET.get('m', ''), 'Invalid message'),
        'user_courses': request.user.course_set.all()
    })


@login_required()
def course_show(request, course_slug):
    course = get_object_or_404(models.Course, name=course_slug)
    if not course.has_user(request.user):
        return redirect(reverse('wui_courses') + "?m=join_first")

    return render(
        request, "courses/detail_course.html",
        {
            'course': course,
            'page': 'course'
        }
    )


@permission_required('can_manage_course')
def course_delete(request, course_slug):
    course = get_object_or_404(models.Course, name=course_slug)
    course.delete()
    return redirect(reverse('wui_courses') + "?m=deleted")


@login_required()
def course_join(request, course_slug):
    course = get_object_or_404(models.Course, name=course_slug)
    if course.password:
        return redirect(
            reverse(
                'wui_course_join_pw',
                kwargs={'course_slug': course_slug}
            )
        )
    course.participants.add(request.user)
    return redirect(reverse('wui_courses') + "?m=joined")


@login_required()
def course_join_pw(request, course_slug):
    course = get_object_or_404(models.Course, name=course_slug)
    msg = ""
    if request.POST:
        form = CoursePwForm(request.POST)
        if form.is_valid():
            if course.password == form.cleaned_data['password']:
                course.participants.add(request.user)
                return redirect(reverse('wui_courses') + "?m=joined")
            else:
                msg = _("Wrong password")
    else:
        msg = _("Enter Password")

    return render(
        request,
        "courses/join_pw.html",
        {
            'msg': msg,
            'form': CoursePwForm()
        }
    )


@login_required()
def course_leave(request, course_slug):
    course = get_object_or_404(models.Course, name=course_slug)
    course.participants.remove(request.user)
    return redirect(reverse('wui_courses') + "?m=left")


@login_required()
def course_scoreboard(request, course_slug):
    return None


@login_required()
def course_problems(request, course_slug):
    return None


@login_required()
def user_problems(request):
    return None


@permission_required('can_manage_course')
def course_manage_problems(request, course_slug):
    course = get_object_or_404(models.Course, name=course_slug)
    if request.POST:
        form = AddProbForm(request.POST, instance=course)
        if form.is_valid():
            models.CourseProblems.drop_for_course(course)
            for problem in form.cleaned_data['problems']:
                models.CourseProblems.create_or_update(course, problem)
            return redirect(reverse('wui_points_to_problems',
                                    kwargs={'course_slug': course_slug}))

    return render(
        request,
        "courses/manage_problems.html",
        {
            "course_name": course.name,
            "form": AddProbForm(instance=course)
        }
    )


@permission_required('can_manage_course')
def course_manage_points(request, course_slug):
    course = get_object_or_404(models.Course, name=course_slug)
    problems = course.problems.all()
    cp_forms = []

    if request.POST:
        for prob in problems:
            form = PointToProbForm(request.POST, prefix=prob.slug)
            cp_forms.append(form)
            if form.is_valid():
                models.CourseProblems.create_or_update(
                    course,
                    prob,
                    form.cleaned_data['points']
                )
            else:
                break
        else:
            return redirect(reverse('wui_courses'))
    else:
        for cp in problems:
            cp_forms.append(PointToProbForm(prefix=cp.slug))

    return render(
        request,
        "courses/manage_points.html",
        {'cp_forms': cp_forms}
    )


def index(request):
    return redirect('pages/')