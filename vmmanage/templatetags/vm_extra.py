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
from django import template
from autotask.models import (
    WAITING,
    RUNNING,
    ERROR,
    DONE
)

from uptomate.Deployment import  VAGRANT_RUNNING_STATES

register = template.Library()

TASK_CSS_CLASSES = {
    WAITING: "active",
    RUNNING: "info",
    ERROR: "danger",
    DONE: "success"
}


@register.filter()
def task_css_class(task_state):
    return TASK_CSS_CLASSES.get(task_state, "")

@register.filter()
def state_css_class(vm_state):
    return "success" if vm_state in VAGRANT_RUNNING_STATES else "danger"


@register.filter()
def joinby(join_list, value):
    return value.join([str(x) for x in join_list])
