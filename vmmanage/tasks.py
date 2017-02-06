# Berlyne IT security trainings platform
# Copyright (C) 2016 Ruben Gonzalez <rg@ht11.org>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
from subprocess import CalledProcessError
from time import sleep

from autotask.tasks import delayed_task
from django.conf import settings

from uptomate import Deployment
from .models import State, UNKNOWN_HOST

MSG_SUCCESS = "Finished"
IN_USE_SLEEP_TIME = 10

@delayed_task(ttl=settings.TASK_TTL)
def run_on_vagr(vagr_depl, f, vm_db, callback=None, **kwargs):
    """
    This runs an action on a vagrant deployment. A action is
    a method defined on vagr_depl. If autotask is active, this
    will be done by a autotask worker.
    :param vagr_depl: the vagrant deployment
    :param f: the action to call
    :param vm_db: the VM ORM object
    :param callback: if not None, callback will be called after the action
    :param kwargs: Arguments to call the callback with
    :return:
    """
    # TODO: Would be better to schedule the other tasks here
    # instead of waiting for the VM to get free
    # Wait until VM is free
    succeed = False
    while not succeed:
        succeed = vm_db.lock()
        sleep(IN_USE_SLEEP_TIME)

    if f != "status":
        try:
            getattr(Deployment.Vagrant, f)(vagr_depl, **kwargs)
        except BaseException:
            vm_db.unlock()
            raise
    if callback:
        callback(vagr_depl, f, vm_db, **kwargs)

    status = vagr_depl.status()
    vm_db.provider = status.provider
    vm_db.state_set.add(State(name=status.state), bulk=False)

    try:
        vm_db.ip_addr = vagr_depl.service_network_address()
    except CalledProcessError:
        # this does not work all the time, e.g. when the command
        # was 'stop', however, that should never affect the
        # result of the actual command called
        vm_db.ip_addr = UNKNOWN_HOST
    vm_db.unlock()
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
def destroy_problem(problem):
    problem.destroy()
    return MSG_SUCCESS
