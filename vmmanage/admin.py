from django.contrib import admin

from .models import *

admin.site.register(VirtualMachine)
admin.site.register(Task)
admin.site.register(Port)
admin.site.register(State)
admin.site.register(Tag)
admin.site.register(Download)