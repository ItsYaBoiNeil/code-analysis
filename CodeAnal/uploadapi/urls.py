from django.urls import path
from . import views

urlpatterns = [
    path('upload/', views.upload_code, name='upload_code'),
]
