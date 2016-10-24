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
]