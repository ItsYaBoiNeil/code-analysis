from django.urls import path
from . import views

urlpatterns = [
    path('', views.upload_code, name='upload_code'),
    path('chat/', views.chat_page, name='chat_page'),
    path('chat_model/', views.chat_with_model, name='chat_with_model'),
]