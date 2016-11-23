from django import template
from autotask.models import (
    WAITING,
    RUNNING,
    ERROR,
    DONE
)
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
