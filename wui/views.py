from django.shortcuts import render, redirect, get_object_or_404
from django.forms import ModelForm, Form, CharField
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


class CoursePwForm(Form):
    password = CharField(label=_('Password'), max_length=255)


MESSAGES = {
    '': None,
    'joined': _("You joined the course"),
    'deleted': _("You deleted the course"),
    'left': _("You left the course"),
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

@login_required()
def courses(request):
    return render(request, 'courses/list.html', {
        'headline': _('Courses'),
        'courses': models.Course.objects.all(),
        'message': MESSAGES.get(request.GET.get('m', ''), 'Invalid message'),
        'user_courses': request.user.course_set.all()
    })


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
def scoreboard(request):
    return None


@login_required()
def problems(request):
    return None


def course_tasks(request):
    return None



def index(request):
    return redirect('pages/')