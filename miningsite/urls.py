"""miningsite URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
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
from django.urls import path, include, reverse_lazy
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.conf.urls import handler404
# For password reset
from django.contrib.auth import views as auth_views

# Default admin site settings
admin.site.site_title = "Mining Admin"
admin.site.site_header = "MINING ADMIN"

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('miningapp.urls')),


    # Password reset paths
    # Don't use reset paths under namespaced url
    # or better still use in projects url 
    
    path('reset-password/', 
    auth_views.PasswordResetView.as_view(
    template_name="password_reset.html",
    success_url=reverse_lazy('password_reset_done')
    ), 
    name="reset_password"),

    path('reset-password-sent/', 
    auth_views.PasswordResetDoneView.as_view(
    template_name="password_reset_sent.html"
    ), 
    name="password_reset_done"),

    path('reset/<uidb64>/<token>/', 
    auth_views.PasswordResetConfirmView.as_view(
    template_name="password_reset_form.html",
    success_url=reverse_lazy('password_reset_complete')
    ), 
    name="password_reset_confirm"),

    path('password-reset-complete', 
    auth_views.PasswordResetCompleteView.as_view(
    template_name="password_reset_complete.html"
    ), 
    name="password_reset_complete"),
]


urlpatterns += static(settings.MEDIA_URL, document_root = settings.MEDIA_ROOT)


# Error page settings
handler404 = 'miningapp.views.error404'
handler500 = 'miningapp.views.error500'
