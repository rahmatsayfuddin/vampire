from django.urls import path
from . import views

urlpatterns = [
    path('', views.project_list, name='project_list'),
    path('create/', views.project_create, name='project_create'),
    path('create/from_product/<int:product_id>/', views.project_create, name='project_create_from_product'),
    path('update/<int:pk>/', views.project_update, name='project_update'),
    path('delete/<int:pk>/', views.project_delete, name='project_delete'),
    path('<int:pk>/', views.project_detail, name='project_detail'),

    path('sla/', views.sla_profile_list, name='sla_profile_list'),
    path('sla/create/', views.sla_profile_create, name='sla_profile_create'),
    path('sla/<int:pk>/edit/', views.sla_profile_update, name='sla_profile_update'),
    path('sla/<int:pk>/delete/', views.sla_profile_delete, name='sla_profile_delete'),
]
