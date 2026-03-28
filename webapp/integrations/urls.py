from django.urls import path

from . import views

app_name = 'integrations'

urlpatterns = [
    path('', views.integration_list, name='integration_list'),
    path('<str:provider>/connect/', views.integration_connect, name='integration_connect'),
    path('<str:provider>/callback/', views.integration_callback, name='integration_callback'),
    path('<str:provider>/select-account/', views.integration_select_account, name='integration_select_account'),
    path('<int:pk>/disconnect/', views.integration_disconnect, name='integration_disconnect'),
]
