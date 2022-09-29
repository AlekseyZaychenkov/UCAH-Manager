from django.contrib.auth import logout, login, authenticate
from django.contrib.auth.hashers import check_password
from django.shortcuts import render, redirect
from account.forms import RegistrationForm, AccountAuthenticationForm
from account.models import Account


def loginView(request):
    context = dict()
    context["email_does_not_exist"] = False
    context["password_is_wrong"] = False

    if 'action' in request.POST and request.POST['action'] == 'go_to_login':
        form = AccountAuthenticationForm(request.POST)
    elif 'email' in request.POST and request.POST:
        context["email"] = request.POST['email']
        email = request.POST['email']
        password = request.POST['password']
        form = AccountAuthenticationForm(request.POST)

        if not Account.objects.filter(email=email).exists():
            context["email_does_not_exist"] = True
        elif not authenticate(email=email, password=password):
            context["password_is_wrong"] = True
        else:
            if form.is_valid():
                user = authenticate(email=email, password=password)
                login(request, user)
                return redirect('workspace')
    else:
        form = AccountAuthenticationForm()

    context['form'] = form

    return render(request, "login.html", context)


def logoutView(request):
    logout(request)
    return redirect("login")


def registerView(request):
    context = {}
    if request.POST:
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('workspace')
    else:
        form = RegistrationForm()
    context['form'] = form
    return render(request, "to_register.html", context)
