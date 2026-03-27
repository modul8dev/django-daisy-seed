from django.urls import path

from . import views

app_name = 'scheduler'

urlpatterns = [
    path('', views.scheduler_view, name='scheduler'),
    path('api/events/', views.scheduler_events, name='scheduler_events'),
    path('api/reschedule/<int:pk>/', views.scheduler_reschedule, name='scheduler_reschedule'),
]
