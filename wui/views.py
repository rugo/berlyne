from django.shortcuts import render, redirect, get_object_or_404
from django.forms import ModelForm
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required, permission_required
from . import models
from django.utils.translation import ugettext_lazy as _
from django.urls import reverse

class UserForm(ModelForm):
    class Meta:
        model = User
        fields = ['email', 'first_name', 'last_name']


class CourseForm(ModelForm):
    class Meta:
        model = models.Course
        fields = [
            'name',
            'description',
            'show_scoreboard',
            'password',
            'point_threshold'
        ]


@login_required()
def profile(request):
    if request.POST:
        form = UserForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
    else:
        form = UserForm(instance=request.user)

    return render(request, 'accounts/profile.html', {'form': form})


@permission_required('can_manage_course')
def course_edit(request, course_slug=None):
    if request.POST:
        form = CourseForm(request.POST)
        if form.is_valid():
            form.instance.teacher = request.user
            form.save()
    else:
        if course_slug:
            form = CourseForm(
                instance=get_object_or_404(models.Course, name=course_slug)
            )
        else:
            form = CourseForm()
    return render(request, 'generic/model_form.html', {'headline': _('Course'),
                                                       'form': form})

@permission_required('can_manage_course')
def courses(request):
    return render(request, 'courses/list.html', {
        'headline': _('Courses'),
        'courses': models.Course.objects.all(),
    })


@permission_required('can_manage_course')
def course_delete(request, course_slug):
    course = get_object_or_404(models.Course, name=course_slug)
    course.delete()
    return redirect(reverse('wui_courses'))

@login_required()
def scoreboard(request):
    return None


@login_required()
def problems(request):
    return None


def course_tasks(request):
    return None



def index(request):
    return redirect('pages/')