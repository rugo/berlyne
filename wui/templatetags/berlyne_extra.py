# Used from:
# https://github.com/ebertti/django-registration-bootstrap
from django import template
register = template.Library()


@register.filter()
def add_class(field, css):
    return field.as_widget(attrs={"class": css})


@register.filter(name='is_in_group')
def user_is_in_group(user, group_name):
    return user.groups.filter(name=group_name).exists()
