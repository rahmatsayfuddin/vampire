from django.urls import path
from . import views

urlpatterns = [
    path('', views.vkb_list, name='vkb_list'),
    path('create/', views.vkb_create, name='vkb_create'),
    path('update/<int:pk>/', views.vkb_update, name='vkb_update'),
    path('delete/<int:pk>/', views.vkb_delete, name='vkb_delete'),
    path('api/<int:pk>/', views.get_vkb_json, name='vkb_api'),

]
