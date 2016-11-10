from django.forms import (
    ModelForm,
    Form,
    CharField,
    IntegerField,
    HiddenInput
)

from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _
from . import models


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


class AddProbForm(ModelForm):
    class Meta:
        model = models.Course
        fields = ["problems"]


class PointToProbForm(Form):
    points = IntegerField()


class SubmissionForm(Form):
    problem_slug = CharField(widget=HiddenInput)
    flag = CharField(max_length=255)