from celery import shared_task
from .uptomate import Deployment
MSG_SUCCESS = "Finished"


@shared_task()
def run_on_vagr(vagr_depl, f, vm_db=None, **kwargs):
    getattr(Deployment.Vagrant, f)(vagr_depl, **kwargs)
    if vm_db is not None:
        vm_db.ip_addr = vagr_depl.service_network_address()
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
    destroy_vm_db(vm)
    vagr_depl.destroy()
    return MSG_SUCCESS
