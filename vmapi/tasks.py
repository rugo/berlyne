from autotask.tasks import delayed_task
from .uptomate import Deployment

MSG_SUCCESS = "Finished"


@delayed_task()
def run_on_vagr(vagr_depl, f, vm_db=None, **kwargs):
    getattr(Deployment.Vagrant, f)(vagr_depl, **kwargs)
    if vm_db is not None:
        try:
            vm_db.ip_addr = vagr_depl.service_network_address()
            vm_db.save()
        except BaseException:
            # this does not work all the time, e.g. when the command
            # was 'stop', however, that should never affect the
            # result of the actual command called
            pass
    return MSG_SUCCESS


@delayed_task()
def status_of_deployment(vagr_depl):
    return vagr_depl.status().state


@delayed_task()
def service_network_address(vagr_depl):
    return vagr_depl.service_network_address()


@delayed_task()
def destroy_vm_db(vm):
    vm.delete()
    return MSG_SUCCESS


@delayed_task()
def destroy_deployment(vagr_depl, vm):
    destroy_vm_db(vm)
    vagr_depl.destroy()
    return MSG_SUCCESS
