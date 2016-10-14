# from __future__ import absolute_import
#
# import os
#
# from celery import Celery
#
#
# # set the default Django settings module for the 'celery' program.
# os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'berlyne.settings')
# from django.conf import settings
#
# app = Celery('berlyne')
#
# # This should be changed to a string on windows
# app.config_from_object('django.conf:settings')
#
# app.autodiscover_tasks(['vmapi'])
#
# @app.task(bind=True)
# def fun(self):
#     with open("/tmp/lol", "w") as f:
#         f.write(b"dsdsdsd")
from __future__ import absolute_import

import os

from celery import Celery

# set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'berlyne.settings')

from django.conf import settings  # noqa

app = Celery('berlyne')

# Using a string here means the worker will not have to
# pickle the object when using Windows.
app.config_from_object('django.conf:settings')
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)
