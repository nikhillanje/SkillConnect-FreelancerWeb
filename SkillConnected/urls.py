from django.urls import path
from SkillConnected import views
from django.conf import settings
from django.conf.urls.static import static,include
from .views import db_check

urlpatterns = [
    path('', views.index, name='index'),
    path('freelancer_Signup/', views.freelancer_Signup, name='freelancer_Signup'),
    path('client_Signup/', views.client_Signup, name='client_Signup'),
    path('db_check/', db_check),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
