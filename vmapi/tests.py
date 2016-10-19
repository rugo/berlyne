from django.test import TestCase, Client
from django.core.urlresolvers import reverse
from unittest import skip
from django.conf import settings
from celery.states import READY_STATES, SUCCESS
import json
from time import sleep
from datetime import datetime
import vmapi.models
import vmapi.views
from urllib.request import urlopen
import os


SLUG = "test"
TEXT = "test"


def _content_as_dict(resp):
    return json.loads(resp.content.decode())


def _task_status_from_resp(resp):
    return _content_as_dict(resp)['state']


def _task_id_from_resp(resp):
    return _content_as_dict(resp)['task_id']


# TODO: Write actual tests
# This can't really considered a test. Most of the class is written to use
# the API via a client and check the tasks results. Unfortunately there is
# no real way to get celery working in the test environment without ugly
# hacking. Which is why celery runs in EAGER mode
# (docs.celeryproject.org/projects/django-celery/en/2.4/
# cookbook/unit-testing.html)
# for the tests which makes the API useless. For now, the tests just call
# the view functions. This should be changed in the future with either making
# celery work with its deamon (maybe an own Runner with keepdb=True?) or
# moving the tests for the api outside of django.

class ApiTest(TestCase):
    def setUp(self):
        self.c = Client()

    def _result_of_task(self, task_id):
        json.loads(self.c.get(reverse(
            'vmapi_task_status',
            kwargs={'task_id': task_id}
        )
        ).content)['result']

    def _wait_until_done(self, task_id, timeout=0):
        resp = self.c.get(reverse("vmapi_task_status",
                                  kwargs={'task_id': task_id}))
        start = datetime.now()
        self.assertEqual(resp.status_code, 200)
        t = _task_status_from_resp(resp)
        while t not in READY_STATES:
            sleep(1)
            t = _task_status_from_resp(resp)
            print(vmapi.models.Task.objects.all())
            if timeout:
                runtime = (datetime.now() - start).total_seconds()
                if runtime > timeout:
                    self.fail("Task with id{} ran into timeout"
                              "after {} seconds".format(task_id, runtime))
        return t

    def _launch_and_wait(self, view_name, **kwargs):
        res = self.c.get(reverse(view_name, kwargs=kwargs))
        self.assertEqual(res.status_code, 200)
        task_id = _task_id_from_resp(res)
        return task_id, self._wait_until_done(task_id)

    def launch_and_check(self, view_name, state, **view_kwargs):
        task_id, s = self._launch_and_wait(view_name, **view_kwargs)
        if isinstance(state, list, tuple):
            return s in state
        return task_id, s == state

    def _assert_view(self, view_name, **kwargs):
        print("Asserting view {}".format(view_name))
        self.assertTrue(
            self.launch_and_check(view_name, SUCCESS, **kwargs)[1]
        )

    def get_ip(self, vm_slug):
        task_id, status = self._launch_and_wait('vmapi_vm_address',
                                                vm_slug=vm_slug)
        self.assertEqual(status, SUCCESS)
        return self._result_of_task(task_id)

    def call_view(self, view_name, **kwargs):
        return self.c.get(reverse(view_name, kwargs=kwargs))

    def check_api(self, vm_slug, vagrant_file, vm_port, vm_text):
        vmapi.views.vm_create(None,
            vm_slug=vm_slug,
            vagrant_name=vagrant_file)

        self.assertTrue(len(vmapi.models.VirtualMachine.objects.all()) == 1)

        self.assertTrue(
            os.path.exists(
                os.path.join(
                    settings.VAGR_DEPLOYMENT_PATH,
                    vm_slug
                )
            )
        )

        vmapi.views.vm_start(None, vm_slug)

        self.assertEqual(
            urlopen(
                "http://{}:{}".format("localhost",
                                      vm_port)
            ).read().decode().strip(),
            vm_text
        )

        vmapi.views.vm_stop(None, vm_slug)

        vmapi.views.vm_destroy(None, vm_slug)

        self.assertFalse(
            os.path.exists(
                os.path.join(
                    settings.VAGR_DEPLOYMENT_PATH,
                    vm_slug
                )
            )
        )

        self.assertTrue(len(vmapi.models.VirtualMachine.objects.all()) == 0)


    def test_docker(self):
        print("Testing docker")
        self.check_api(SLUG, "ubuntu_docker", 8080, TEXT)

    def test_virtualbox(self):
        print("Testing vbox")
        self.check_api(SLUG, "ubuntu_virtualbox", 8080, TEXT)

    @skip("Provision doesnt work yet")
    def test_digital_ocean(self):
        print("Testing digital_ocean")
        self.check_api(SLUG, "ubuntu_digital_ocean", 80, TEXT)

