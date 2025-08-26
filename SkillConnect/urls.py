"""
URL configuration for SkillConnect project.

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
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from SkillConnected import views   # 👈 direct import from your app

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.index, name='index'),
    path('role/', views.role, name='role'),
    path('freelancer_Signup/', views.freelancer_Signup, name='freelancer_Signup'),
    path('client_Signup/', views.client_Signup, name='client_Signup'),
    path("login/", views.login, name="login"),
    path("freelancer/home/", views.freelancer_home, name="freelancerHome"),
    path("client/home/", views.client_home, name="clientHome"),
    path("logout/", views.user_logout, name="logout"),
    path("profile/<int:freelancer_id>/", views.freelancer_profile, name="freelancer_profile"),
    path("profile/client/<int:client_id>/", views.client_profile, name="client_profile"),
    path("freelancer_profile_setup/", views.freelancer_profile_setup, name="freelancer_profile_setup"),
    path("client_profile_setup/", views.client_profile_setup, name="client_profile_setup"),
    path('profile/update-picture/', views.update_profile_picture, name='update_profile_picture'),
    
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)