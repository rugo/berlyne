from django.conf.urls import url, include
from . import views

urlpatterns = [
    url(r'^vm/(?P<vm_slug>[\w-]+)/',
        include(
            [
                url(r'^tasks$', views.vm_tasks, name="vmapi_vm_tasks"),
                url(r'^create/(?P<vagrant_name>[\w-]+)', views.vm_create, name="vmapi_vm_create"),
                url(r'action/(?P<action_name>[\w-]+)', views.vm_action, name='vmapi_vm_action'),
                url(r'^action/start/(?P<provider>[\w-]+)',
                    views.vm_start_provider, name="vmapi_vm_start_prov"),
                url(r'^destroy$', views.vm_destroy, name="vmapi_vm_destroy"),
                url(r'^destroy_db$', views.vm_destroy_db, name="vmapi_vm_destroy_db"),
                url(r'^destroy_fs$', views.vm_destroy_fs, name="vmapi_vm_destroy_fs"),
            ]
            ),
        ),
    url(r'^task/(?P<task_id>[\w-]+)/',
        include(
            [
                url(r'status$', views.task_state, name="vmapi_task_status"),
            ]
            ),
        ),
]
