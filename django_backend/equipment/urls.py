from django.urls import path
from .views import register, upload_csv, history, check_username

urlpatterns = [
    path('register/', register),
    path('check-username/', check_username),
    path('upload/', upload_csv),
    path('history/', history),
]
