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
def status_of_deployment(vagr_depl):
    return vagr_depl.status().state


@shared_task()
def service_network_address(vagr_depl):
    return vagr_depl.service_network_address()


@shared_task()
def destroy_vm_fs(vagr_depl):
    vagr_depl.destroy()
    return MSG_SUCCESS


@shared_task()
def destroy_vm_db(vm):
    vm.delete()
    return MSG_SUCCESS


@shared_task()
def destroy_deployment(vagr_depl, vm):
    destroy_vm_fs(vagr_depl)
    destroy_vm_db(vm)
    return MSG_SUCCESS
