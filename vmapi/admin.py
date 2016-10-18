from django.contrib import admin

from djcelery.models import TaskMeta
from .models import *

admin.site.register(VirtualMachine)
admin.site.register(TaskMeta)
admin.site.register(Task)
