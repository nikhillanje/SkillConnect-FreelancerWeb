from django.urls import path
from SkillConnected import views
from django.conf import settings
from django.conf.urls.static import static,include

urlpatterns = [
    path('', views.index, name='index'),
    path('freelancer_Signup/', views.freelancer_Signup, name='freelancer_Signup'),
    path('client_Signup/', views.client_Signup, name='client_Signup'),
   path("send-otp/", views.send_otp, name="send_otp"),
    path("verify-otp/", views.verify_otp, name="verify_otp"),

]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
