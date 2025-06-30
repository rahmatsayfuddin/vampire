from django.urls import path
from . import views

urlpatterns = [
    path('', views.project_list, name='project_list'),
    path('create/', views.project_create, name='project_create'),
    path('create/from_product/<int:product_id>/', views.project_create, name='project_create_from_product'),
    path('update/<int:pk>/', views.project_update, name='project_update'),
    path('delete/<int:pk>/', views.project_delete, name='project_delete'),
    path('<int:pk>/', views.project_detail, name='project_detail'),

]
