from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('update-bot/', views.register_bot, name='register_bot')
]