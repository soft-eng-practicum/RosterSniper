from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.core.mail import EmailMultiAlternatives
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils.encoding import force_bytes, force_text
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode

from .models import User
from .forms import MyUserCreationForm, UserUpdateForm
from .tokens import account_activation_token


# Auto login after register: stackoverflow.com/a/3222558
def register(request):
    if request.method == 'POST':
        form = MyUserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            
            new_user = authenticate(
                email=form.cleaned_data['email'],
                password=form.cleaned_data['password1'])
            login(request, new_user)

            send_email_verification(new_user)
            messages.info(request, 'Thanks for registering. Please confirm your email to continue.')

            return redirect('add_courses')
    else:
        form = MyUserCreationForm()

    return render(request, 'registration/register.html', {'form': form})


def send_verification(request):
    send_email_verification(request)
    messages.info(request, 'A verification email has been sent.')
    return redirect('profile')


# Not a view
def send_email_verification(request):

    user = request.user

    uid = urlsafe_base64_encode(force_bytes(user.pk))
    token = account_activation_token.make_token(user)
    link = request.build_absolute_uri(reverse('activate', args=[uid, token]))

    context = {
        'name': user.first_name or request.user.username,
        'link': link
    }
    email_text = render_to_string('verification_email.txt', context)
    email_html = render_to_string('verification_email.html', context)
    
    EmailMultiAlternatives(
        subject = "Verify your RosterSniper account",
        to = [user.email],
        body = email_text,
        alternatives = [(email_html, "text/html")]
    ).send()


# https://medium.com/@frfahim/django-registration-with-confirmation-email-bb5da011e4ef
def activate(request, uidb64, token):
    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.emailConfirmed = True
        user.save()
        login(request, user)
        messages.info(request, 'Your email address has been verified!')
        return redirect('profile')
    else:
        return render(request, 'base/message.html', {
            'title': 'Activation Error',
            'message': 'Your activation link is invalid! 😕'
        })


@login_required
def profile(request):
    if request.method == 'POST':
        u_form = UserUpdateForm(request.POST, instance=request.user)

        if u_form.is_valid():
            if 'email' in u_form.changed_data:
                request.user.emailConfirmed = False
            u_form.save()
            messages.success(request, 'Your account has been updated.')
            return redirect('profile')

    else:
        u_form = UserUpdateForm(instance=request.user)

    return render(request, 'registration/profile.html', {'u_form': u_form})
