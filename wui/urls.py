from django.conf.urls import url, include
from . import views

urlpatterns = [
    url(r'^accounts/', include(
        [
            url(r'^profile', views.profile, name='wui_acc_profile'),
            url(r'^', include('django.contrib.auth.urls')),
        ]
    ))
]