from django.urls import path
from . import views

urlpatterns = [
    path('add/<int:project_id>/', views.add_assignment, name='add_assignment'),
    path('remove/<int:assignment_id>/', views.remove_assignment, name='remove_assignment'),
]
