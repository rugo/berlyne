from django.db import models

# TODO: Align to new best practice (pass the instance)
from celery import current_app
from celery.states import READY_STATES, EXCEPTION_STATES

from .uptomate import Deployment

DEFAULT_TASK_NAME = "unnamed_task"


class VirtualMachine(models.Model):
    slug = models.SlugField(unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    ip_addr = models.CharField(max_length=45)
    desc = models.TextField(max_length=1024)

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
    task_id = models.CharField(max_length=255, unique=True)
    # Task name is by default not persistent unfort.
    # So it's stored here
    task_name = models.CharField(max_length=255)
    creation_date = models.DateTimeField(auto_now_add=True)

    # Factory method
    @classmethod
    def create(cls, virtual_machine, async_result):
        return cls(virtual_machine=virtual_machine,
                   task_id=async_result.id,
                   task_name=async_result.task_name or DEFAULT_TASK_NAME)

    @classmethod
    def create_and_launch(cls, virtual_machine, task, **task_kwargs):
        """
        Creates an entry and launches the task
        :param virtual_machine: vm to link to
        :param task: task to run
        :param task_kwargs: task arguments
        :return: Task instance
        """
        return Task.create(virtual_machine, task.delay(**task_kwargs))

    @staticmethod
    def get_nondb_task(task_id):
        """
        Returns state of task that is not stored in db.
        This doesn't happen except somebody played with
        the DB or called destroy_vm_db.

        It is not guaranteed that the task with the given task_id
        exists in case its state returned is PENDING.
        :param task_id: Task_id to look for
        :return: Dict with task info
        """
        return Task._create_basic_task_dict(task_id)

    @staticmethod
    def _create_basic_task_dict(task_id, json_parsable=True):
        task = current_app.AsyncResult(task_id)
        task_dict = {
            'task_name': DEFAULT_TASK_NAME,
            'task_id': task.id,
            'state': task.state
        }

        if task.state in READY_STATES:
            res = task.result
            task_dict['result'] = str(res) if json_parsable else res
        if task.state in EXCEPTION_STATES:
            res = task.traceback
            task_dict['taceback'] = str(res) if json_parsable else res

        return task_dict

    def to_dict(self, json_parsable=True):
        task_dict = Task._create_basic_task_dict(self.task_id, json_parsable)
        vm = self.virtual_machine
        task_dict['vm'] = str(vm) if json_parsable else vm
        task_dict['task_name'] = self.task_name

        return task_dict

    def __str__(self):
        return "<Task: {}>".format(self.task_id)
