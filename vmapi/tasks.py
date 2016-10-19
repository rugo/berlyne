from celery import shared_task
from .uptomate import Deployment
MSG_SUCCESS = "Finished"


@shared_task()
def run_on_vagr(vagr_depl, f):
    getattr(Deployment.Vagrant, f)(vagr_depl)
    return MSG_SUCCESS


@shared_task()
def status_of_deployment(vagr_depl):
    return vagr_depl.status().state


@shared_task()
def service_network_address(vagr_depl):
    return vagr_depl.service_network_address()


@shared_task()
def destroy_vm_db(vm):
    vm.delete()
    return MSG_SUCCESS


@shared_task()
def destroy_deployment(vagr_depl, vm):
    vagr_depl.destroy()
    destroy_vm_db(vm)
    return MSG_SUCCESS
