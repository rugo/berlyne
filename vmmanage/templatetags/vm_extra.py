from django import template
from autotask.models import (
    WAITING,
    RUNNING,
    ERROR,
    DONE
)

from vmmanage.models import VAGRANT_RUNNING_STATES

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
