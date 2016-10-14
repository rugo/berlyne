from django.db import models
from djcelery.models import TaskMeta


class VirtualMachine(models.Model):
    slug = models.SlugField(unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.slug

# Fucked Up
class Task(models.Model):
    virtual_machine = models.ForeignKey(VirtualMachine, on_delete=models.CASCADE)
    task_meta = models.ForeignKey(TaskMeta, to_field="task_id")

    def __str__(self):
        return self.task_meta_id