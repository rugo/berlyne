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
import logging
import string
from collections import defaultdict
from random import randint, choice as rand_choice

from autotask import models as task_models
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.db import models, transaction
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _

from uptomate import Deployment
from uptomate.Provider import LOCALHOST, ALLOWED_PROVIDERS

LEGAL_API_VM_ACTIONS = [
    'start',
    'stop',
    'status',
    # 'address',
    'resume',
    'suspend',
    'reload'
]

MIN_PORT = 1025
MAX_PORT = 2**16-1

RANDOM_FLAG_TEMPLATE = "flag{{{}}}"
FLAG_FILE_NAME = "flag.txt"
RANDOM_FLAG_CHARS = string.ascii_letters + string.digits
RANDOM_FLAG_LEN = 24

UNKNOWN_HOST = "*unknown*"

DEFAULT_TASK_NAME = "unnamed_task"
TASK_STATUS_NAMES = dict(task_models.STATUS_CHOICES)

# Get an instance of a logger
logger = logging.getLogger(__name__)

class VirtualMachine(models.Model):
    slug = models.SlugField(unique=True)
    name = models.CharField(_("name"), max_length=255, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    ip_addr = models.CharField(_("IP Address"), max_length=45)
    provider = models.CharField(max_length=255)

    # Attrs used from config
    desc = models.TextField(_("description"), max_length=1024)
    category = models.CharField(_("Category"), max_length=255)
    flag = models.CharField(max_length=255)
    default_points = models.PositiveSmallIntegerField(default=0)

    # This should only be modified using the
    # lock() and unlock() method
    locked = models.BooleanField(default=False)

    # Stores config of problem running on this machine
    __vagr_config = None
    __vagr_instance = None

    class Meta:
        ordering = ("slug", )

    def predict_state(self):
        """
        Predict the state the VM will be in after its tasks are done.
        Since there might be multiple workers, this should be used
        in a atomic DB block in case the state should be manipulated.
        :return: predicted state
        """
        ts = self.task_set.filter(
            task__status__in=[
                task_models.RUNNING,
                task_models.WAITING
            ]
        ).order_by('-task__scheduled')
        for t in ts:
            # Move down the task stack until one is found that changes the state
            try:
                return Deployment.ASSOCIATED_STATES[t.task_name]
            except KeyError:
                pass
        # if no state manipulating task is found, return the current state
        try:
            return self.state_set.latest().name
        except ObjectDoesNotExist:
            # No state, means somebody messed around with the DB
            # return not_created, so actions will called anyways
            return Deployment.VAGRANT_UNKNOWN

    def lock(self):
        with transaction.atomic():
            self.refresh_from_db()
            if self.locked:
                return False
            self.locked = True
            self.save()
        return True

    def unlock(self):
        self.locked = False
        self.save()

    def get_vagrant(self):
        if not self.__vagr_instance:
            self.__vagr_instance = vagr_factory(self.slug)
        return self.__vagr_instance

    def __get_problem_config(self):
        if not self.__vagr_config:
            self.__vagr_config = self.get_vagrant().get_config()
        return self.__vagr_config.copy()

    def get_problem_config(self):
        return self.__get_problem_config()

    def add_task(self, task, task_name=None):
        self.task_set.add(Task.create(self, task, task_name), bulk=False)

    def set_align_config(self, config):
        config['ports'] = self.__assign_ports(config['ports'])
        self.name = config['name']
        self.desc = config['desc']
        self.category = config['category']
        self.default_points = config['points']
        config['flag'] = self.assign_flag(config.get('flag', ''))

        self.save()

        for t in config['tags']:
            self.tag_set.add(Tag.objects.update_or_create(name=t)[0])

        if 'downloads' in config:
            for slug, d in config['downloads'].items():
                if not slug.isalnum():
                    raise ValueError(
                        "Download slug '{}' is not alphanumeric.".format(
                            slug
                        )
                    )
                self.download_set.add(
                    Download.objects.create(
                        slug=slug,
                        problem=self,
                        path=self.get_vagrant().normalize_content_path(
                            d
                        )
                    )
                )
        return config

    def has_task_in_queue(self, task_name):
        return self.task_set.filter(
                task_status__in=[task_models.WAITING, task_models.RUNNING]
        ).filter(
            task_name=task_name
        ).exists()

    @property
    def is_running(self):
        return self.state_set.latest().name in Deployment.VAGRANT_RUNNING_STATES

    def assign_flag(self, flag):
        """
        Assigns flag or creates one if flag is empty.
        :return: flag that was set
        """
        if not flag:
            flag = VirtualMachine.create_random_flag()
        self.flag = flag
        return flag

    @staticmethod
    def create_random_flag():
        return RANDOM_FLAG_TEMPLATE.format(
            "".join(
                [rand_choice(RANDOM_FLAG_CHARS) for _ in range(RANDOM_FLAG_LEN)]
            )
        )

    def __assign_ports(self, ports):
        for port in ports:
            with transaction.atomic():
                if not port['host']:
                    port['host'] = Port.random_port()
                Port.objects.create(
                    guest_port=port['guest'],
                    host_port=port['host'],
                    description=port['desc'],
                    vm=self
                )
        return ports

    def parse_desc(self):
        if not self.provider or self.ip_addr == UNKNOWN_HOST:
            return None
        ctx = {
            'HOST': settings.DOMAIN if self.ip_addr == LOCALHOST else self.ip_addr
        }

        try:
            provider = ALLOWED_PROVIDERS[self.provider]
        except KeyError:
            logger.warning(
                "Illegal provider '%s' used in VM %s",
                self.provider, self.slug
            )
            return None

        for port in self.port_set.all():
            if provider.port_forwarding:
                ctx['PORT_{}'.format(port.guest_port)] = port.host_port
            else:
                ctx['PORT_{}'.format(port.guest_port)] = port.guest_port

        for download in self.download_set.all():
            ctx['DL_{}'.format(download.slug)] = reverse(
                'wui_download_file',
                kwargs={'download_id': download.pk}
            )
        return self.desc.format_map(defaultdict(str, **ctx))

    def __str__(self):
        return "{}[{}] ({}) - {}".format(
            self.name, self.default_points, self.category,
            ",".join([str(t) for t in self.tag_set.all()])
        )


class Download(models.Model):
    slug = models.SlugField()
    problem = models.ForeignKey(VirtualMachine)
    path = models.CharField(max_length=4096)

    @property
    def abspath(self):
        vagr = self.problem.get_vagrant()
        return vagr.normalize_content_path(
            self.path,
            absolut=True
        )

    class Meta:
        unique_together = ('problem', 'slug')

    def __str__(self):
        return self.path

class Tag(models.Model):
    name = models.SlugField(_("name"), unique=True)
    vm = models.ManyToManyField(VirtualMachine)

    def __str__(self):
        return self.name


class Port(models.Model):
    host_port = models.IntegerField(_("host port"), unique=True)
    guest_port = models.IntegerField(_("guest port"), )
    description = models.CharField(_("description"), max_length=255)
    vm = models.ForeignKey(VirtualMachine, on_delete=models.CASCADE)

    @staticmethod
    def random_port():
        """
        Gets a free port num. This is not thread save and has to be used
        within an atomic block together with the creation of the port obj.
        :return:
        """
        used = Port.objects.all().values_list('host_port', flat=True)

        p = randint(MIN_PORT, MAX_PORT)
        while p in used:
            p = randint(MIN_PORT, MAX_PORT)
        return p

    def __str__(self):
        return "{}->{}:{}".format(self.host_port, self.vm.slug, self.guest_port)


class State(models.Model):
    name = models.CharField(_("name"), max_length=255)
    created = models.DateTimeField(auto_now_add=True)
    vm = models.ForeignKey(VirtualMachine)

    class Meta:
        get_latest_by = "created"
        ordering = ["-created"]

    def __str__(self):
        return self.name


class Task(models.Model):
    """
    Used to link a task to a virtual machine.
    This should always be created using the factory methods
    given.
    """
    virtual_machine = models.ForeignKey(VirtualMachine, on_delete=models.CASCADE)
    task = models.ForeignKey(task_models.TaskQueue)
    task_name = models.CharField(_("name"), max_length=255)
    creation_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        get_latest_by = "creation_date"
        ordering = ["-creation_date"]

    # Factory method
    @classmethod
    def create(cls, virtual_machine, task, task_name=None):
        if not task_name:
            task_name = task.function_name
        return cls(virtual_machine=virtual_machine,
                   task_id=task.pk,
                   task_name=task_name)

    @classmethod
    def create_and_launch(cls, virtual_machine, task, **task_kwargs):
        """
        Creates an entry and launches the task
        :param virtual_machine: vm to link to
        :param task: task to run
        :param task_kwargs: task arguments
        :return: Task instance
        """
        return Task.create(virtual_machine, task(**task_kwargs))

    def get_state_name(self):
        return TASK_STATUS_NAMES[self.task.status]

    def to_dict(self, json_parsable=True):
        task_dict = {
            'task_name': self.task.function,
            'task_id': self.task.pk,
            'state': self.get_state_name()
        }

        res = None
        if self.task.status == task_models.DONE:
            res = self.task.result
        if self.task.status == task_models.ERROR:
            res = self.task.error_message
        if res is not None:
            task_dict['result'] = str(res) if json_parsable else res

        vm = self.virtual_machine
        task_dict['vm'] = str(vm) if json_parsable else vm

        return task_dict

    def __str__(self):
        return "{} [{}]".format(self.task_name, TASK_STATUS_NAMES[self.task.status])


def vagr_factory(vm_slug):
    return Deployment.Vagrant(
        vm_slug,
        deployment_path=settings.VAGR_DEPLOYMENT_PATH,
    )
