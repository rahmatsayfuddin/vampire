from django.urls import path
from . import views

urlpatterns = [
    # User URLs
    path('users/', views.user_list, name='user_list'),
    path('users/create/', views.user_create, name='user_create'),
    path('users/<int:pk>/edit/', views.user_update, name='user_update'),
    path('users/<int:pk>/delete/', views.user_delete, name='user_delete'),

    # Group URLs
    path('roles/', views.group_list, name='group_list'),
    path('roles/create/', views.group_create, name='group_create'),
    path('roles/<int:pk>/edit/', views.group_update, name='group_update'),
    path('roles/<int:pk>/delete/', views.group_delete, name='group_delete'),
]
