# Berlyne IT security trainings platform
# Copyright (C) 2016 Ruben Gonzalez <rg@ht11.org>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
from http.client import NOT_FOUND as HTTP_NOT_FOUND
from os import path
from wsgiref.util import FileWrapper

from django.contrib.auth.decorators import login_required, permission_required
from django.db import IntegrityError
from django.db.models import (
    Sum,
    Max,
    Case,
    When,
    F,
    Value
)
from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _

from vmmanage import views as vm_views
from vmmanage.models import Download
from .forms import *

DOWNLOAD_FNAME_TEMLATE = "{problem_slug}_{download_pk}_{filename}"
MESSAGES = {
    '': None,
    'joined': _("You joined the course"),
    'deleted': _("You deleted the course"),
    'left': _("You left the course"),
    'join_first': _("Join the course first"),
    'problem_not_ready': _("The problem has not been initialized yet")
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
            form = CourseForm(
                initial={
                    'start_time': timezone.now(),
                    'deadline': timezone.now() + timezone.timedelta(weeks=1)
                }
            )
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
    vm_views.stop_unused_vms(course.problems.all())
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
    return redirect(reverse('wui_course_show', kwargs={'course_slug': course_slug}))


@login_required()
def course_join_pw(request, course_slug):
    course = get_object_or_404(models.Course, name=course_slug)
    msg = ""
    if request.POST:
        form = CoursePwForm(request.POST)
        if form.is_valid():
            if course.password == form.cleaned_data['password']:
                course.participants.add(request.user)
                return redirect(reverse(
                    'wui_course_show', kwargs={'course_slug': course_slug})
                )
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


def _course_problem_dict(course, user):
    categories = {}
    total_points = 0
    for course_prob in models.CourseProblems.objects.filter(course=course):
        category = course_prob.problem.category.capitalize()
        problems = categories.get(category, [])

        problems.append({
            'title': course_prob.problem.name,
            'slug': course_prob.problem.slug,
            'points': course_prob.points,
            'desc': course_prob.problem.parse_desc() or
                        MESSAGES['problem_not_ready'],
            'form': SubmissionForm(initial={
                'problem_slug': course_prob.problem.slug}
            ),
            'solved_count': course_prob.submission_set.filter(
                correct=True
            ).count(),
            'solved': course_prob.submission_set.filter(
                user=user,
                correct=True,
            ).exists()
        })

        total_points += course_prob.points
        # In case new list was created
        categories[category] = problems
    return categories, total_points


# TODO: put in fewer queries and split view
@login_required()
def course_problems(request, course_slug):
    course = get_object_or_404(models.Course, name=course_slug)
    if not course.has_begun and course.teacher != request.user:
        return redirect(
            reverse('wui_course_show', kwargs={'course_slug': course_slug})
        )
    open_slug = request.GET.get('slug', '')
    errors = []
    success = []
    if not course.has_user(request.user):
        return redirect(reverse('wui_courses') + "?m=join_first")

    if request.POST:
        if course.has_ended:
            errors.append(_("The course is over."))
        else:
            form = SubmissionForm(request.POST)
            if form.is_valid():
                flag_correct, course_problem =\
                    models.CourseProblems.check_problem_flag(
                        course,
                        form.cleaned_data['problem_slug'],
                        form.cleaned_data['flag']
                    )
                try:
                    models.Submission.objects.create(
                        flag=form.cleaned_data['flag'],
                        problem=course_problem,
                        correct=flag_correct,
                        user=request.user
                    )
                    if flag_correct and course.writeups:
                        return redirect(
                            reverse(
                                'wui_course_problem_writeup',
                                kwargs={
                                    'course_slug': course_slug,
                                    'problem_slug': course_problem.problem.slug
                                }
                            )
                        )
                except IntegrityError:
                    errors.append(_("You already tried that..."))

                if flag_correct:
                    success.append(_("Flag was correct!"))
                else:
                    errors.append(_("Flag was incorrect!"))
            else:
                errors.append(_("Form was invalid"))

    categories, total_points = _course_problem_dict(course, request.user)
    user_points = sum(
        [
            sub.problem.points for sub in models.Submission.objects.filter(
                user=request.user,
                correct=True,
                problem__course=course
            )
        ]
    )

    return render(
        request,
        "courses/course_problems.html",
        {
            'categories': categories,
            'total_points': total_points,
            'user_points': user_points,
            'page': 'problems',
            'course': course,
            'open_slug': open_slug,
            'errors': errors,
            'success': success
        }
    )


@login_required()
def course_scoreboard(request, course_slug):
    course = get_object_or_404(models.Course, name=course_slug)

    # Create list with user and points
    user_points = course.participants.values(
        'username',
        'last_name'
    ).annotate(
        point_sum=Sum(
            Case(
                When(
                    submission__correct=True,
                    then=F('submission__problem__points'),
                ),
                default=Value(0),
            )
        )
    ).annotate(
        newest_submission=Max('submission__creation_time')
    ).exclude(
        username__exact=course.teacher.username
    ).order_by(
        '-point_sum',
        'newest_submission'
    )

    return render(
        request,
        'courses/scoreboard.html',
        {
            'course': course,
            'user_points': enumerate(user_points, 1),
            'page': 'scoreboard'
        }
    )


@permission_required('can_manage_course')
def course_manage_problems(request, course_slug):
    course = get_object_or_404(models.Course, name=course_slug)
    errors = []
    if request.POST:
        form = AddProbForm(request.POST, instance=course)
        if form.is_valid():
            new_problems = form.cleaned_data['problems']

            removed_problems = models.CourseProblems.objects.filter(
                course=course,
                problem__virtualmachine__isnull=False
            ).exclude(problem__in=new_problems)

            vm_views.stop_unused_vms([p.problem.vm for p in removed_problems])

            removed_problems.delete()

            for problem in new_problems:
                models.CourseProblems.objects.update_or_create(
                    course=course, problem=problem, defaults={'points': problem.default_points}
                )

            new_problem_vms = []
            for p in new_problems:
                if p.vm:
                    new_problem_vms.append(p.vm)

            vm_views.start_used_vms(new_problem_vms)
            return redirect(reverse('wui_points_to_problems',
                                    kwargs={'course_slug': course_slug}))
        else:
            errors.append("Select at least one valid problem")

    return render(
        request,
        "courses/manage_problems.html",
        {
            "errors": errors,
            "course_name": course.name,
            "form": AddProbForm(instance=course)
        }
    )


@permission_required('can_manage_course')
def course_manage_points(request, course_slug):
    course = get_object_or_404(models.Course, name=course_slug)
    problems = models.CourseProblems.objects.filter(course=course)
    cp_forms = []

    if request.POST:
        for prob in problems:
            form = PointToProbForm(request.POST, prefix=prob.problem.slug)
            cp_forms.append(form)
            if form.is_valid():
                models.CourseProblems.objects.filter(
                    course=course,
                    problem=prob.problem
                ).update(
                    points=form.cleaned_data['points']
                )
            else:
                break
        else:
            return redirect(reverse('wui_courses'))
    else:
        for cp in problems:
            cp_forms.append(
                PointToProbForm(
                    prefix=cp.problem.slug,
                    initial={'points': cp.points}
                )
            )

    return render(
        request,
        "courses/manage_points.html",
        {'cp_forms': cp_forms}
    )


@login_required()
def writeup(request, course_slug, problem_slug):
    course = get_object_or_404(models.Course, name=course_slug)
    if course.has_ended or not course.has_begun:
        return redirect('wui_course_show', kwargs={"course_slug": course_slug})
    submission = get_object_or_404(
        models.Submission,
        problem__problem__slug=problem_slug,
        correct=True,
        user=request.user,
    )

    if not course.writeups:
        return redirect('wui_course_show', kwargs={"course_slug": course_slug})

    form = WriteupForm(instance=submission)

    if request.POST:
        form = WriteupForm(request.POST, instance=submission)
        if form.is_valid():
            form.save()
            return redirect(
                reverse(
                    'wui_course_problems',
                    kwargs={
                        'course_slug': course.name
                    }
                ) + '?slug=' + problem_slug
            )

    return render(
        request,
        'courses/writeup.html',
        {
            'course': course,
            'form': form,
        }
    )


def register(request):
    form = UserEmailCreateForm()
    if request.POST:
        form = UserEmailCreateForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('wui_courses')
    return render(request, "registration/register.html", {'form': form})


@permission_required('can_manage_course')
def course_writeups(request, course_slug):
    course = get_object_or_404(models.Course, name=course_slug)
    submissions = models.Submission.objects.filter(
        writeup__isnull=False,
        problem__course=course
    ).values(
        'problem__problem__slug',
        'creation_time',
        'user__username',
        'user__last_name'
    ).order_by(
        'problem__problem__slug',
        'creation_time'
    )

    errors = []

    if not course.writeups:
        errors.append(_("Write ups are disabled for this course"))

    return render(
        request,
        'courses/show_writeups.html',
        {
            'submissions': submissions,
            'errors': errors,
            'page': "writeups",
            'course': course
        }
    )


@permission_required('can_manage_course')
def show_writeup(request, course_slug, problem_name, user_name):
    sub = get_object_or_404(
        models.Submission,
        user__username=user_name,
        problem__problem__slug=problem_name,
        problem__course__name=course_slug,
        correct=True
    )

    return render(
        request,
        'courses/show_writeup.html',
        {
            "sub": sub
        }
    )


def _download_wrapped_file(download):
    download_path = download.abspath
    if not path.exists(download_path):
        return HttpResponse("Download not found", status=HTTP_NOT_FOUND)
    wrapper = FileWrapper(open(download_path, "rb"))
    response = HttpResponse(wrapper, content_type='application/force-download')
    response['Content-Disposition'] = 'attachment; filename="{}"'.format(
        DOWNLOAD_FNAME_TEMLATE.format(
            filename=path.basename(download_path),
            download_pk=download.pk,
            problem_slug=download.problem.slug
        )
    )
    response['Content-Length'] = path.getsize(download_path)
    return response


@login_required()
def download_file(request, download_id):
    download = get_object_or_404(Download, pk=download_id)

    if download.problem.course_set.filter(
            participants__pk=request.user.pk
    ).exists():
            return _download_wrapped_file(download)

    return HttpResponse(
        "Not Found", status=HTTP_NOT_FOUND
    )


def index(request):
    return redirect('pages/')
