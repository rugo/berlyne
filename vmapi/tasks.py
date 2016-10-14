from celery import shared_task
from time import sleep

# simulate long running task
@shared_task()
def create_deployment(vagr_depl):
    sleep(15)
    vagr_depl.create()
    return True
