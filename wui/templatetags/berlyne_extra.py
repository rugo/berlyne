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
from markdown import markdown

register = template.Library()

# Uses code from:
# https://github.com/ebertti/django-registration-bootstrap
@register.filter()
def add_class(field, css):
    return field.as_widget(attrs={"class": css})


@register.filter()
def has_perm(user, perm_name):
    return user.has_perm(perm_name)


@register.filter(name='is_in_group')
def user_is_in_group(user, group_name):
    return user.groups.filter(name=group_name).exists()


@register.filter()
def markdownify(text):
    return markdown(text)

