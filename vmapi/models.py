from django.db import models

from autotask import models as task_models
from autotask.tasks import DelayedTask
from .uptomate import Deployment

DEFAULT_TASK_NAME = "unnamed_task"


class VirtualMachine(models.Model):
    slug = models.SlugField(unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    ip_addr = models.CharField(max_length=45)

    # Attrs used from config
    desc = models.TextField(max_length=1024)
    category = models.CharField(max_length=255)
    flag = models.CharField(max_length=255)

    # Stores config of problem running on this machine
    __vagr_config = None

    def __get_problem_config(self):
        if not self.__vagr_config:
            vagr = Deployment.Vagrant(self.slug)
            self.__vagr_config = vagr.get_config()
        return self.__vagr_config.copy()

    def get_problem_config(self):
        return self.__get_problem_config()

    def add_task(self, async_result):
        self.task_set.add(Task.create(self, async_result), bulk=False)

    def __str__(self):
        return self.slug


class Port(models.Model):
    number = models.IntegerField(primary_key=True)
    vm = models.ForeignKey(VirtualMachine, on_delete=models.CASCADE)


class Task(models.Model):
    """
    Used to link a task to a virtual machine.
    This should always be created using the factory methods
    given.
    """
    virtual_machine = models.ForeignKey(VirtualMachine, on_delete=models.CASCADE)
    task = models.ForeignKey(task_models.TaskQueue)
    creation_date = models.DateTimeField(auto_now_add=True)

    # Factory method
    @classmethod
    def create(cls, virtual_machine, task):
        return cls(virtual_machine=virtual_machine,
                   task_id=task.pk)

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

    def to_dict(self, json_parsable=True):
        task_dict = {
            'task_name': self.task.function,
            'task_id': self.task.pk,
            'state': self.task.status
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
        return "<Task: {}>".format(self.task_id)
