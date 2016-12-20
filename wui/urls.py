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
    url(r'^$', views.index, name='wui_index'),
    url(r'^pages/', include('django.contrib.flatpages.urls')),
    url(r'^accounts/', include(
        [
            url(r'^profile/$', views.profile, name='wui_acc_profile'),
            url(r'^register/$', views.register, name='wui_acc_register'),
            url(r'^', include('django.contrib.auth.urls')),
        ]
    )),
    url(r'^course_create/$', views.course_edit, name='wui_course_create'),
    url(r'^course/$', views.courses, name='wui_courses'),
    url(r'^course/(?P<course_slug>[\w-]+)/', include(
        [
            url(r'^edit/$', views.course_edit, name='wui_course_edit'),
            url(r'^$', views.course_show, name='wui_course_show'),
            url(r'^delete/$', views.course_delete, name='wui_course_delete'),
            url(r'^join/$', views.course_join, name='wui_course_join'),
            url(r'^join_pw/$', views.course_join_pw, name='wui_course_join_pw'),
            url(r'^leave/$', views.course_leave, name='wui_course_leave'),
            url(r'^problems/$', views.course_problems, name='wui_course_problems'),
            url(r'^problem_writeup/(?P<problem_slug>[\w-]+)/$', views.writeup, name='wui_course_problem_writeup'),
            url(r'^scoreboard/$', views.course_scoreboard, name='wui_course_scoreboard'),
            url(r'^manage_problems/$', views.course_manage_problems, name='wui_course_manage_problems'),
            url(r'^manage_points/$', views.course_manage_points, name='wui_points_to_problems'),
            url(r'^writeups/$', views.course_writeups, name='wui_course_writeups'),
            url(r'^writeups/(?P<problem_name>[\w-]+)/(?P<user_name>[\w-]+)/$', views.show_writeup, name='wui_course_writeup_show')
        ]
    )),
    url(r'^downloads/(?P<download_id>[\w-]+)/$', views.download_file, name='wui_download_file'),
]
