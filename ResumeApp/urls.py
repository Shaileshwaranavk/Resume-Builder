from django.urls import path
from .views import RegisterView, LoginView, ResumeView, ResumeDocxDownloadView

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('resume/', ResumeView.as_view(), name='resume'),
    path('resume/download/', ResumeDocxDownloadView.as_view(), name='resume_download'),
]
