import os
import shutil
import json
import yaml
import time
from subprocess import CalledProcessError, check_output
from .Provider import ALLOWED_PROVIDERS


CONFIG_FILE_NAME = "docker-compose.yml"
TASK_CONTENT_FILE_NAME = "task.zip"
DEFAULT_FILE_NAMES = [CONFIG_FILE_NAME, "setup", TASK_CONTENT_FILE_NAME]
VAGRANTFILE_NAME = "Vagrantfile"
INSTALLED_MARKER_FILE = "installed"
PORTS_CONFIG_FILE = "ports.json"
PROBLEM_FOLDER_NAME = "problem"

INSTANCE_DIR_NAME = "instance"
CONTENT_DIR_NAME = "."

_DEFAULT_DIR_MODE = 0o770

# Unfort. some vagrant plugins use different names for
# the same thing. With this table, the status names are unified.
_STATUS_TRANSLATION = {
    # digital ocean plugin has status "active" for "running"
    'active': 'running',
    # VirtualBox says "poweroff" instead of "stopped"
    'poweroff': 'stopped'
}

VAGRANT_RUNNING = 'running'
VAGRANT_STOPPED = 'stopped'
VAGRANT_NOT_CREATED = "not_created"
VAGRANT_UNKNOWN = "**unknown**"
VAGRANT_RUNNING_STATES = (VAGRANT_RUNNING,)
VAGRANT_STOPPED_STATES = (VAGRANT_STOPPED, VAGRANT_NOT_CREATED)
VAGRANT_STATES = VAGRANT_RUNNING_STATES + VAGRANT_STOPPED_STATES

# Which action causes which state
ASSOCIATED_STATES = {
    'start': VAGRANT_RUNNING,
    'stop': VAGRANT_STOPPED,
    'install': VAGRANT_NOT_CREATED,
    'reload': VAGRANT_RUNNING,
}

# Codes vagrant uses when some or all of the destroy commands
# where declined:
# github.com/mitchellh/vagrant/blob/master/plugins/commands/destroy/command.rb
_DECL_RETCODES = [1, 2]

_joinp = os.path.join
_p_exists = os.path.exists


def _fname(path):
    return os.path.split(path)[-1]


def _move_files(files_dict, dst_folder):
    for f in files_dict:
        f_name = _joinp(dst_folder, _fname(f))

        shutil.move(f, f_name)


def _make_absolute(path):
    if path.startswith("/"):
        return path
    return _joinp(os.getcwd(), path)


def check_installed(method):
    def creator(self, *args, **kwargs):
        if self.installed:
            return method(self, *args, **kwargs)
        else:
            raise ValueError(
                "Deployment '{}' is not installed yet!".format(self)
            )
    return creator


class Vagrant:

    def __init__(self,
                 name,
                 deployment_path="deployments"):
        self.__name = name
        self.__base_path = _joinp(os.path.abspath(deployment_path), name)
        self.__content_path = _joinp(self.__base_path, CONTENT_DIR_NAME)
        self.__installed_marker = _joinp(self.__base_path, INSTALLED_MARKER_FILE)

    def call_dc(self, command, *args):
        args = " ".join(args)
        cli = f"cd {self.__base_path} && docker-compose {command} {args}"
        try:
            return check_output(cli, shell=True)
        except CalledProcessError as ex:
            raise ValueError(f"Could not finish {command} {args}: {ex}")

    def install(self):
        if not _p_exists(self.__base_path):
            raise ValueError(
                "No Deployment with name '{}' exists!".format(self.__name)
            )

        self.call_dc("build")

    @property
    def exists(self):
        return os.path.exists(self.__base_path)

    @property
    def installed(self):
        # App, docker-compose doesn't have a way to list already build images
        try:
            service_image_names = self.call_dc("config", "--images").decode().split()

            if len(service_image_names) < 1:
                raise ValueError("Can't determine installed status as service has no images. "
                                 "Most likely a download-only service.")
            first_service_name = service_image_names[0]
            check_output(f"docker images|grep {first_service_name}", shell=True)

            return True
        except CalledProcessError:
            return False

    @check_installed
    def start(self, provider=None):
        self.call_dc("up", "-d")

        for _ in range(30):
            if self.status() == "running":
                break
            # Docker-Compose doesnt offer a sane way to get the information...
            time.sleep(10)
        else:
            raise ValueError("Containers did not start.")

    def get_config(self):
        try:
            with open(_joinp(self.__base_path, CONFIG_FILE_NAME)) as f:
                c = yaml.safe_load(f)["x-task-meta"]
        except OSError:
            raise ValueError("No configfile exists in {}".format(self.path))
        except (TypeError, ValueError) as ex:
            raise ValueError("Config file invalid: {}".format(str(ex)))

        return c

    def normalize_dl_path(self, rel_path, absolut=False):
        """
        Normalizes the given relative path and checks if
        rel_path is in content dir, to avoid path traversal.
        :param rel_path: relative path in content dir
        :param absolut: if True, return absolut path to re_path
        :return: normalized path to rel_path
        """
        dl_folder = self.__base_path
        full_path = _joinp(
            dl_folder,
            rel_path
        )
        norm_path = os.path.normpath(
            full_path
        )
        if not norm_path.startswith(dl_folder):
            raise ValueError(
                "Path '{}' is not inside '{}'s content dir".format(
                    dl_folder, self.__name
                )
            )

        if absolut:
            return norm_path

        return norm_path[len(dl_folder)+1:]

    def open_content_file(self, file_name, mode="w"):
        """
        Opens a file in the deployments content dir.
        :return: File handle
        """
        return open(_joinp(self.__content_path, file_name), mode)

    @check_installed
    def stop(self):
        self.call_dc("down")

    @check_installed
    def resume(self):
        self.call_dc("unpause")

    @check_installed
    def reload(self):
        self.destroy()
        self.start()

    @check_installed
    def rebuild(self):
        prev_status = self.status()

        self.destroy()
        self.install()

        if prev_status == VAGRANT_RUNNING:
            self.start()

    @check_installed
    def suspend(self):
        self.call_dc("pause")

    @check_installed
    def status(self):
        possible_states = ["running", "stopped", "paused"]
        for state in possible_states:
            out = self.call_dc("ps", "--services", f'--filter "status={state}"')
            if len(out) > 1:
                return state
        if self.installed:
            return VAGRANT_NOT_CREATED
        return "unknown"

    @check_installed
    def find_provider(self):
        """
        Tries to get the provider from vagrant.
        If that fails, None is returned
        :return: Provider or None
        """
        return ALLOWED_PROVIDERS["docker-compose"]

    @check_installed
    def hostname(self):
        return "localhost"

    @check_installed
    def service_network_address(self):
        """
        Tries to get the services address.
        If no provider can be found, None is returned
        :return: Address as string or None
        """
        provider = self.find_provider()
        if not provider:
            return None
        return provider.get_accessible_address(self.hostname())

    @check_installed
    def destroy(self):
        self.call_dc("down", "--rmi all")

    def __str__(self):
        return "Compose: '{}'".format(self.__name)