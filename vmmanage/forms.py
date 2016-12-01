from django.forms import Form, ChoiceField, ModelForm
from . import deploy_controller
from . import models


class VagrantFilesForm(Form):
    vagrant_file = ChoiceField(label="Deployment evnironment",
        choices=[(x, x)for x in deploy_controller.get_avail_vagrant_files()],
    )


class ProblemEditForm(ModelForm):
    class Meta:
        model = models.VirtualMachine
        fields = ["name", "desc", "category"]