from django.urls import path
from . import views

urlpatterns = [
    path('', views.finding_list, name='finding_list'),
    path('create/<int:project_id>/', views.create_finding, name='create_finding'),
    path('<int:pk>/', views.finding_detail, name='finding_detail'),
    path('<int:pk>/edit/', views.edit_finding, name='finding_edit'),  # next
    path('<int:pk>/delete/', views.delete_finding, name='finding_delete'),  # next
]
