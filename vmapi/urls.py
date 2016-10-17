from django.conf.urls import url, include
from . import views

urlpatterns = [
    url(r'^(?P<vm_slug>[\w-]+)/', include(
        [
            url(r'^status$', views.vm_status),
            url(r'^tasks$', views.vm_tasks),
            url(r'^create/(?P<vagrant_name>[\w-]+)', views.vm_create),
            url(r'^start/(?P<provider>[\w-]+)', views.vm_start),
            url(r'^start$', views.vm_start),
            url(r'^stop$', views.vm_stop),
            url(r'^destroy$', views.vm_destroy),
        ]
    )),
]