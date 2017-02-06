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
from django.forms import Form, ChoiceField, ModelForm

from . import deploy_controller
from . import models


class VagrantFilesForm(Form):
    vagrant_file = ChoiceField(label="VM deployment",
        choices=[(x, x)for x in deploy_controller.get_avail_vagrant_files()]
    )


class ProblemEditForm(ModelForm):
    class Meta:
        model = models.Problem
        fields = ["name", "desc", "category"]