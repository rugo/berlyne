from django.db import models
from djcelery.models import TaskMeta


class VirtualMachine(models.Model):
    slug = models.SlugField(unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def add_task(self, async_result):
        self.task_set.add(Task.create(self, async_result), bulk=False)

    def __str__(self):
        return self.slug

# Fucked Up
class Task(models.Model):
    virtual_machine = models.ForeignKey(VirtualMachine, on_delete=models.CASCADE)
    task_meta = models.ForeignKey(TaskMeta, to_field="task_id")
    task_name = models.CharField(max_length=200)
    creation_date = models.DateTimeField(auto_now_add=True)

    # Factory method
    @classmethod
    def create(cls, virtual_machine, async_result):
        return cls(virtual_machine=virtual_machine, task_meta_id=async_result.id, task_name=async_result.task_name)

    def to_dict(self):
        task_meta_dict = self.task_meta.to_dict()
        task_meta_dict['date_done'] = str(task_meta_dict['date_done'])
        task_meta_dict['task_name'] = self.task_name
        task_meta_dict['result'] = str(task_meta_dict['result'])
        del(task_meta_dict['children'])
        return task_meta_dict

    def __str__(self):
        return self.task_meta_id