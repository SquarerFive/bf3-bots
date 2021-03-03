from django.urls import path
from django.conf.urls import url
from . import views

urlpatterns = [
    path('project/<int:project_id>/level/<int:level_id>/uei-gtm/', views.uei_gtm, name='uei-gtm'),
]