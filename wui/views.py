from django.shortcuts import render, redirect
from django.forms import ModelForm
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required


class UserForm(ModelForm):
     class Meta:
         model = User
         fields = ['email', 'first_name', 'last_name']


@login_required()
def profile(request):
    if request.POST:
        form = UserForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
    else:
        form = UserForm(instance=request.user)

    return render(request, 'accounts/profile.html', {'form': form})


@login_required()
def scoreboard(request):
    return None


@login_required()
def problems(request):
    return None

def index(request):
    return redirect('pages/')