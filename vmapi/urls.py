from django.conf.urls import url, include
from . import views

urlpatterns = [
    url(r'^vm/(?P<vm_slug>[\w-]+)/',
        include(
            [
                url(r'^status$', views.vm_status, name="vmapi:vm_status"),
                url(r'^address$', views.vm_address, name="vmapi:vm_address"),
                url(r'^tasks$', views.vm_tasks, name="vmapi:vm_tasks"),
                url(r'^create/(?P<vagrant_name>[\w-]+)', views.vm_create, name="vmapi:vm_create"),
                url(r'^start/(?P<provider>[\w-]+)', views.vm_start, name="vmapi:vm_start_prov"),
                url(r'^start$', views.vm_start, name="vmapi:vm_start"),
                url(r'^stop$', views.vm_stop, name="vmapi:vm_stop"),
                url(r'^destroy$', views.vm_destroy, name="vmapi:vm_destroy"),
                url(r'^destroy_db$', views.vm_destroy_db, name="vmapi:vm_destroy_db"),
                url(r'^destroy_fs$', views.vm_destroy_fs, name="vmapi:vm_destroy_fs"),
            ]
            ),
        ),
    url(r'^task/(?P<task_id>[\w-]+)',
        include(
            [
                url(r'status$', views.task_state, name="vmapi:task_status"),
            ]
            ),
        ),
]
