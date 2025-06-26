"""
URL configuration for mysite project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.shortcuts import render
from django.urls import path, include
from django.conf.urls.static import static
from django.conf import settings
from users.views import profile_view,confirm_email,CustomPasswordResetView,CustomPasswordResetConfirmView
from django.contrib.auth import views as auth_views
from django.views.generic import TemplateView

def test_404(request):
    return render(request, '404.html', status=404)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('account/password_reset/', CustomPasswordResetView.as_view(), name='password_reset'),
    path('account/password_reset/done/', auth_views.PasswordResetDoneView.as_view(template_name='registration/password_reset_done.html'), name='password_reset_done'),
    path('account/reset/<uidb64>/<token>/', CustomPasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('account/reset/done/', auth_views.PasswordResetCompleteView.as_view(template_name='registration/password_reset_complete.html'), name='password_reset_complete'),

    path('account/confirm-email/<str:key>/', confirm_email, name="confirm-email"),
    path('account/', include('allauth.urls')),
    path('account/',include('django.contrib.auth.urls')),
    path('',include('chat_application.urls')),
    path('profile/', include('users.urls')),
    path('profile/<str:username>/',profile_view,name="profile"),
    path('force-404/', test_404),
    
]

urlpatterns += [
    path('test/', TemplateView.as_view(template_name="registration/password_reset_form.html")),
]

if settings.DEBUG:
    urlpatterns +=static(settings.MEDIA_URL,document_root=settings.MEDIA_ROOT)
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

handler404 = 'mysite.views.custom_404'
