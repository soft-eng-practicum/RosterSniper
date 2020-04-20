from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.utils.encoding import force_bytes, force_text
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.contrib.auth.models import User
from django.template.loader import get_template
from django.core.mail import EmailMultiAlternatives

from .token import account_activation_token
from .forms import MyUserCreationForm, UserUpdateForm, ProfileUpdateForm


# stackoverflow.com/a/3222558
def register(request):
    if request.method == 'POST':
        form = MyUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False
            user.save()
            context = {
                'name': form.cleaned_data.get('first_name') or form.cleaned_data.get('username'),
                'hostname': 'rsniper.shitchell.com',
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': account_activation_token.make_token(user)
            }
            email_text = get_template('verification_email.txt')
            email_html = get_template('verification_email.html')
            email_text = email_text.render(context)
            email_html = email_html.render(context)
            
            subject = f"Verify your Roster Sniper account"
            addr_to = form.cleaned_data.get('email')
            addr_from = "Roster Sniper <no-reply@shitchell.com>"
            msg = EmailMultiAlternatives(subject, email_text, addr_from, [addr_to])
            msg.attach_alternative(email_html, "text/html")
            msg.send()

            messages.info(request, 'Thanks for registering. Please confirm your email to continue.')
            return redirect('login')
            #new_user = authenticate(username=form.cleaned_data['username'],
            #                        password=form.cleaned_data['password1'])

            #login(request, new_user)
            #return redirect('add_course')
    else:
        form = MyUserCreationForm()

    return render(request, 'register.html', {'form': form})

# https://medium.com/@frfahim/django-registration-with-confirmation-email-bb5da011e4ef
def activate(request, uidb64, token):
    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.save()
        login(request, user)
        messages.info(request, 'Your email address has been verified!')
        return redirect('profile')
    else:
        return HttpResponse('Activation link is invalid!')

@login_required
def profile(request):
    if request.method == 'POST':
        u_form = UserUpdateForm(request.POST, instance=request.user)
        p_form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user.profile)

        if u_form.is_valid() and p_form.is_valid():
            u_form.save()
            p_form.save()
            messages.success(request, 'Your account has been updated.')
            return redirect('profile')

    else:
        u_form = UserUpdateForm(instance=request.user)
        p_form = ProfileUpdateForm(instance=request.user.profile)

    context = {'u_form': u_form, 'p_form': p_form}

    return render(request, 'profile.html', context)
