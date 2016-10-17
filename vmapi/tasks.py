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


@shared_task()
def stop_deployment(vagr_depl):
    vagr_depl.stop()
    return MSG_SUCCESS


@shared_task()
def destroy_deployment(vagr_depl, vm):
    vagr_depl.destroy()
    vm.delete()
    return MSG_SUCCESS