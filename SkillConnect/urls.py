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
from SkillConnected import views
from SkillConnected.views import db_check

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
    path("send-otp/", views.send_otp, name="send_otp"),
    path("verify-otp/", views.verify_otp, name="verify_otp"),
    path('post-job/<int:client_id>/', views.post_job, name='postJob'),
    path("apply/<int:job_id>/", views.apply_job, name="apply_job"),
    path('client/applied-jobs/', views.client_applied_jobs, name='client_applied_jobs'),
    path('client/update-status/<int:applied_job_id>/<str:status>/', views.update_application_status, name='update_application_status'),
    path('freelancer/notifications/', views.freelancer_notifications, name='freelancer_notifications'),
    path('chat/<str:receiver_type>/<int:receiver_id>/', views.chat_view, name='chat_view'),
    path('chat/send/', views.send_chat_ajax, name='send_chat_ajax'),
    path('chat/fetch/<str:receiver_type>/<int:receiver_id>/', views.fetch_chat_ajax, name='fetch_chat_ajax'),
    path('client/messages/', views.client_chat_list, name='client_chat_list'),
    path('client/messages/<int:freelancer_id>/', views.client_chat_view, name='client_chat_view'),
    path('freelancer/messages/', views.freelancer_chat_list, name='freelancer_chat_list'),
    path('freelancer/messages/<int:client_id>/', views.freelancer_chat_view, name='freelancer_chat_view'),
    path("freelancer/<int:freelancer_id>/view/", views.freelancer_profile_view, name="freelancer_profile_view"),
    path('client/view/<int:client_id>/', views.client_profile_view, name='client_profile_view'),
    path('client/your-posted-jobs/', views.client_posted_jobs, name='client_posted_jobs'),
    path('client/delete-job/<int:job_id>/', views.delete_posted_job, name='delete_posted_job'),
    path('freelancer/job/<int:job_id>/', views.freelancer_job_detail, name='freelancer_job_detail'),
    path('client/edit-job/<int:job_id>/', views.edit_posted_job, name='edit_posted_job'),
    path('feedback/', views.give_feedback, name='give_feedback'),
    path("client/notifications/", views.notifications_view, name="notifications_view"),
    path("client/overview/", views.client_overview, name="client_overview"),
    path('companies/', views.companies_page, name='companies_page'),
    path('ai-tools/', views.ai_tools, name='ai_tools'),
    path("freelancer/recommendations/", views.job_recommendations, name="job_recommendations"),
    path("generate-interview-questions/", views.generate_interview_questions, name="generate_interview_questions"),
    path('analyze-resume/', views.analyze_resume, name='analyze_resume'),
    path('help-support/', views.help_support, name='help_support'),
    path('db_check/', db_check),

]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)