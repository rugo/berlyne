from autotask.tasks import delayed_task
from uptomate import Deployment
from django.conf import settings
from .models import State
from subprocess import CalledProcessError

MSG_SUCCESS = "Finished"


@delayed_task(ttl=settings.TASK_TTL)
def run_on_vagr(vagr_depl, f, vm_db=None, callback=None, **kwargs):
    if f != "status":
        getattr(Deployment.Vagrant, f)(vagr_depl, **kwargs)
    if callback:
        callback(vagr_depl, f, vm_db, **kwargs)
    if vm_db is not None:
        vm_db.state_set.add(State(name=vagr_depl.status().state), bulk=False)
        try:
            vm_db.ip_addr = vagr_depl.service_network_address()
        except CalledProcessError:
            # this does not work all the time, e.g. when the command
            # was 'stop', however, that should never affect the
            # result of the actual command called
            vm_db.ip_addr = "Unknown"
        vm_db.save()
    return MSG_SUCCESS


@delayed_task(ttl=settings.TASK_TTL)
def status_of_deployment(vagr_depl):
    return vagr_depl.status().state


@delayed_task(ttl=settings.TASK_TTL)
def service_network_address(vagr_depl):
    return vagr_depl.service_network_address()


@delayed_task(ttl=settings.TASK_TTL)
def destroy_vm_db(vm):
    vm.delete()
    return MSG_SUCCESS


@delayed_task(ttl=settings.TASK_TTL)
def destroy_deployment(vagr_depl, vm):
    destroy_vm_db(vm)
    vagr_depl.destroy()
    return MSG_SUCCESS
