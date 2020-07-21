from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.core.mail import EmailMultiAlternatives
from django.shortcuts import render, redirect
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode

from core.utils import full_reverse

from .models import User
from .forms import MyUserCreationForm, UserUpdateForm
from .tokens import activation_token_generator


def register(request):

    if request.method == 'POST':
        form = MyUserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            
            # Auto login after register: stackoverflow.com/a/3222558
            new_user = authenticate(
                email=form.cleaned_data['email'],
                password=form.cleaned_data['password1'])
            login(request, new_user)

            send_email_verification(new_user)
            messages.info(request, 'Thanks for registering. Please confirm your email to receive notifications.')

            return redirect('profile')

    elif request.is_ajax() and request.GET.get('send_email'):
        send_email_verification(request.user)
        messages.info(request, 'A verification email has been sent.')
        return redirect('profile')

    else:
        form = MyUserCreationForm()

    return render(request, 'registration/register.html', {'form': form})


# Not a view
def send_email_verification(user):

    uid = urlsafe_base64_encode(force_bytes(user.pk))
    token = activation_token_generator.make_token(user)

    context = {
        'home': full_reverse('home'),
        'link': full_reverse('activate', args=[uid, token])
    }
    email_text = render_to_string('emails/verification.txt', context)
    email_html = render_to_string('emails/verification.html', context)
    
    EmailMultiAlternatives(
        subject = "Verify your RosterSniper account",
        to = [user.email],
        body = email_text,
        alternatives = [(email_html, "text/html")]
    ).send()


# https://medium.com/@frfahim/django-registration-with-confirmation-email-bb5da011e4ef
def activate(request, uidb64, token):

    try:
        user = User.objects.get(
            pk=force_str(urlsafe_base64_decode(uidb64))
        )

    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        pass

    else:
        if activation_token_generator.check_token(user, token):
            user.email_confirmed = True
            user.save()
            messages.info(request, 'Your email address has been verified!')
            return redirect('profile')

    return render(request, 'base/message.html', {
        'title': 'Activation Error',
        'message': 'Your activation link is invalid! 😕'
    })


@login_required
def profile(request):

    if request.method == 'POST':
        form = UserUpdateForm(request.POST, instance=request.user)

        if form.is_valid():
            if 'email' in form.changed_data:
                request.user.email_confirmed = False
                request.user.save()
                
            form.save()
            messages.success(request, 'Your account has been updated.')
            return redirect('profile')

    else:
        form = UserUpdateForm(instance=request.user)

    return render(request, 'registration/profile.html', {'form': form})
