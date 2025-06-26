from django.shortcuts import render, redirect,HttpResponse
from django.urls import reverse
from allauth.account.utils import send_email_confirmation
from allauth.account.models import EmailConfirmationHMAC
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout,get_user_model
from django.contrib.auth.models import User
from django.http import HttpResponse,Http404
from django.contrib import messages
from .forms import ProfileForm, EmailForm
from django.contrib.auth.views import PasswordResetView,PasswordResetConfirmView
from django.urls import reverse_lazy
from django.utils.http import urlsafe_base64_decode
from django.utils.encoding import force_str


def profile_view(request, username=None):
    if username:
        try:
            profile = User.objects.get(username=username).profile
        except User.DoesNotExist:
            raise Http404("User does not exist")
    else:
        try:
            profile=request.user.profile
        except:
            return redirect('account_login')
    return render(request, 'users/profile.html', {'profile': profile})


@login_required
def profile_edit_view(request):
    profile = request.user.profile  # Get the user's profile instance

    # Determine if the user is on the onboarding path
    onboarding = request.path == reverse('profile-onboarding')

    if request.method == 'POST':
        # Bind form with POST and FILES (for image upload)
        form = ProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()  # Save updated profile; old image cleanup handled by django-cleanup
            return redirect('profile')
    else:
        # Display form with current profile data
        form = ProfileForm(instance=profile)

    return render(request, 'users/profile_edit.html', {
        'form': form,
        'onboarding': onboarding
    })

@login_required
def profile_settings_view(request):
    return render(request,'users/profile_settings.html')


@login_required
def profile_emailchange(request):
    print("Inside confirm_email view!") 
    if request.htmx:
        form=EmailForm(instance=request.user)
        return render(request,'partial/email_form.html',{'form':form})
    if request.method=='POST':
        form=EmailForm(request.POST,instance=request.user)
        if form.is_valid():
            email=form.cleaned_data['email']
            if User.objects.filter(email=email).exclude(id=request.user.id).exists():
                messages.warning(request,f'{email} is already in use.')
                return redirect('profile-settings')
            form.save()
            send_email_confirmation(request,request.user)
            return redirect('profile-settings')
        else:
            messages.warning(request,'Form not valid')
            return redirect('profile-settings')
    return redirect('home')

@login_required
def profile_emailverify(request):
    send_email_confirmation(request,request.user)
    return redirect('profile-settings')

@login_required
def profile_delete_view(request):
    user=request.user
    if request.method=="POST":
        logout(request)
        user.delete()
        messages.success(request,'Account delete, what a pity')
        return redirect('home')
        
    return render(request,'users/profile_delete.html')


def confirm_email(request, key):
    confirmation = EmailConfirmationHMAC.from_key(key)

    if not confirmation:
        return HttpResponse("Invalid confirmation link", status=400)

    if request.method == 'POST':
        confirmation.confirm(request)
        messages.success(request, "Email address confirmed successfully.")
        return redirect('profile-settings')  # or wherever you want to redirect

    return render(request, 'account/confirm-email.html', {
        'email': confirmation.email_address.email,
        'user': confirmation.email_address.user,
    })


# users/views.py

User = get_user_model()

class CustomPasswordResetView(PasswordResetView):
    template_name = 'registration/password_reset_form.html'
    email_template_name = 'registration/password_reset_email.html'
    success_url = reverse_lazy('password_reset_done')

    def get_email_context(self):
        context = super().get_email_context()
        context['domain'] = self.request.get_host()
        context['protocol'] = 'http'  # Force HTTP in development
        print("📧 Password reset email context:", context)
        return context

class CustomPasswordResetConfirmView(PasswordResetConfirmView):
    template_name = 'registration/password_reset_confirm.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            uid = force_str(urlsafe_base64_decode(self.kwargs.get("uidb64")))
            user = User.objects.get(pk=uid)
            context['email'] = user.email
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            context['email'] = None
        return context