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
from django.conf.urls import url, include

from . import views

urlpatterns = [
    url(r"^problem/", include([
        url(r'^install/$', views.show_installable_problems, name="vmmanage_show_installable"),
        url(r'^install_problem/$', views.install_problem, name="vmmanage_install_problem"),
        url(r'^problem/(?P<problem_slug>[\w-]+)/', include([
            url(r'^$', views.problem_detail, name="vmmanage_detail_problem"),
            url(r'^action/(?P<action_name>[\w-]+)$',
                views.perform_action, name="vmmanage_perform_action"),
            url(r'destroy/$', views.problem_destroy, name='vmmanage_problem_destroy'),
            url(r'^edit/$', views.edit_problem, name="vmmanage_edit_problem"),
        ])),
    ])),
    url(r'problems/$', views.problem_overview, name="vmmanage_show_problems"),
]
