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
from django.forms import (
    ModelForm,
    Form,
    CharField,
    IntegerField,
    HiddenInput,
    EmailField
)
from django.contrib.auth.forms import (
    UserCreationForm,
    UsernameField
)
from django.contrib.admin.widgets import FilteredSelectMultiple
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
            'writeups',
            'start_time',
            'deadline',
            'password',
            'point_threshold',
        ]
        labels = {
            'point_threshold': "Points required (may be 0)"
        }


class CoursePwForm(Form):
    password = CharField(label=_('Password'), max_length=255)


class AddProbForm(ModelForm):
    class Meta:
        model = models.Course
        fields = ("problems",)
        widgets = {'problems': FilteredSelectMultiple("Problems", False)}


class PointToProbForm(Form):
    points = IntegerField()


class SubmissionForm(Form):
    problem_slug = CharField(widget=HiddenInput)
    flag = CharField(max_length=255)


class WriteupForm(ModelForm):
    class Meta:
        model = models.Submission
        fields = ('writeup',)


class UserEmailCreateForm(UserCreationForm):
    class Meta:
        model = User
        fields = ("username", "email")
        field_classes = {
            'username': UsernameField,
            'email': EmailField
        }
