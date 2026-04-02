from django.urls import path

from . import views

app_name = 'campaigns'

urlpatterns = [
    path('', views.chat_view, name='chat'),
    path('<int:conversation_id>/', views.chat_view, name='chat_conversation'),
    path('conversations/create/', views.conversation_create, name='conversation_create'),
    path('conversations/<int:pk>/delete/', views.conversation_delete, name='conversation_delete'),
    path('conversations/<int:conversation_id>/messages/', views.conversation_messages, name='conversation_messages'),
    path('conversations/<int:conversation_id>/send/', views.send_message, name='send_message'),
    path('conversations/<int:conversation_id>/drafts/<int:draft_id>/approve/', views.approve_campaign, name='approve_campaign'),
]
