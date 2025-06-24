# roles/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.role_list, name='role_list'),
    path('create/', views.role_create, name='role_create'),
    path('update/<int:pk>/', views.role_update, name='role_update'),
    path('delete/<int:pk>/', views.role_delete, name='role_delete'),
    path('<int:pk>/', views.role_detail, name='role_detail'),
    path('<int:role_id>/remove_menu/<int:menu_id>/', views.remove_menu_from_role, name='remove_menu_from_role'),
]
