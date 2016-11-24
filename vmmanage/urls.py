from django.conf.urls import url, include
from . import views

urlpatterns = [
    url(r'^api/', include([
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
    ])),
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
