from celery import shared_task

MSG_SUCCESS = "Finished"

@shared_task()
def create_deployment(vagr_depl):
    vagr_depl.create()
    return MSG_SUCCESS

@shared_task()
def start_deployment(vagr_depl):
    vagr_depl.start()
    return MSG_SUCCESS