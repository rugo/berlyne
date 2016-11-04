from django.conf.urls import url, include
from . import views

urlpatterns = [
    url(r'^$', views.index, name='wui_index'),
    url(r'^pages/', include('django.contrib.flatpages.urls')),
    url(r'^accounts/', include(
        [
            url(r'^profile/$', views.profile, name='wui_acc_profile'),
            url(r'^', include('django.contrib.auth.urls')),
        ]
    )),
    url(r'^scoreboard/$', views.scoreboard, name='wui_scoreboard'),
    url(r'^problems/$', views.problems, name='wui_problems'),
    url(r'^course_create$', views.course_edit, name='wui_course_create'),
    url(r'^course/$', views.courses, name='wui_courses'),
    url(r'^course/(?P<course_slug>[\w-]+)/edit/$', views.course_edit, name='wui_course_edit'),
    url(r'^course/(?P<course_slug>[\w-]+)/$', views.course_show, name='wui_course_show'),
    url(r'^course/(?P<course_slug>[\w-]+)/tasks/$', views.course_tasks, name='wui_course_tasks'),
    url(r'^course/(?P<course_slug>[\w-]+)/delete/$', views.course_delete, name='wui_course_delete'),
    url(r'^course/(?P<course_slug>[\w-]+)/join/$', views.course_join, name='wui_course_join'),
    url(r'^course/(?P<course_slug>[\w-]+)/join_pw/$', views.course_join_pw, name='wui_course_join_pw'),
    url(r'^course/(?P<course_slug>[\w-]+)/leave/$', views.course_leave, name='wui_course_leave'),
]