from django.conf.urls import url, include
from . import views

urlpatterns = [
    url(r'^(?P<vm_slug>[\w-]+)/', include(
        [
            url(r'^status$', views.vm_status),
            url(r'^create/(?P<vagrant_name>[\w-]+)', views.vm_create)
        ]
    )),
]