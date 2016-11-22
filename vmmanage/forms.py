from django.forms import Form, ChoiceField
from . import deploy_controller


class VagrantFilesForm(Form):
    vagrant_file = ChoiceField(
        choices=[(x, x)for x in deploy_controller.get_avail_vagrant_files()],
    )