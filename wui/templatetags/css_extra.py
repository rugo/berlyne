# Used from:
# https://github.com/ebertti/django-registration-bootstrap
from django import template
register = template.Library()

@register.filter()
def add_class(field, css):
   return field.as_widget(attrs={"class":css})