from django.contrib import admin
from . import signals
from . import models

admin.site.register(models.Course)
admin.site.register(models.CourseProblems)
admin.site.register(models.Submission)
