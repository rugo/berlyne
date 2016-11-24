from django.db import models, transaction
from autotask import models as task_models
from uptomate import Deployment
from random import randint, choice as rand_choice
from django.utils.translation import ugettext_lazy as _
import string

MIN_PORT = 1025
MAX_PORT = 2**16-1

RANDOM_FLAG_TEMPLATE = "flag{{{}}}"
RANDOM_FLAG_CHARS = string.ascii_letters + string.digits
RANDOM_FLAG_LEN = 24

DEFAULT_TASK_NAME = "unnamed_task"
TASK_STATUS_NAMES = dict(task_models.STATUS_CHOICES)


class VirtualMachine(models.Model):
    slug = models.SlugField(unique=True)
    name = models.CharField(_("name"), max_length=255, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    ip_addr = models.CharField(_("IP Address"), max_length=45)

    # Attrs used from config
    desc = models.TextField(_("description"), max_length=1024)
    category = models.CharField(_("Category"), max_length=255)
    flag = models.CharField(max_length=255)
    default_points = models.PositiveSmallIntegerField(default=0)

    # Stores config of problem running on this machine
    __vagr_config = None

    def __get_problem_config(self):
        if not self.__vagr_config:
            vagr = Deployment.Vagrant(self.slug)
            self.__vagr_config = vagr.get_config()
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
        for t in config['tags']:
            self.tag_set.add(Tag.objects.update_or_create(name=t)[0])
        self.save()
        return config

    def assign_flag(self, flag):
        """
        Assigns flag or creates one if flag is empty.
        :return: flag that was set
        """
        if not flag:
            flag = self.create_random_flag()
        self.flag = flag
        return flag

    def create_random_flag(self):
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

    def __str__(self):
        return self.slug


class Tag(models.Model):
    name = models.SlugField(_("name"), unique=True)
    vm = models.ManyToManyField(VirtualMachine)

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
        return "{}->{}:{}".format(self.host_port, self.vm, self.guest_port)



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
