from django.urls import path

from . import views

app_name = 'media_library'

urlpatterns = [
    path('create/', views.image_group_create, name='image_group_create'),
    path('add-url-image/', views.add_url_image, name='add_url_image'),
    path('import-products/', views.products_import, name='products_import'),
    path('import-url/', views.url_import, name='url_import'),
    path('image-editor/', views.image_editor_modal, name='image_editor_modal'),
    path('image-editor/generate/', views.image_editor_generate, name='image_editor_generate'),
    path('<int:pk>/edit/', views.image_group_edit, name='image_group_edit'),
    path('<int:pk>/delete/', views.image_group_delete, name='image_group_delete'),
    path('image-picker/', views.image_picker, name='image_picker'),
]
