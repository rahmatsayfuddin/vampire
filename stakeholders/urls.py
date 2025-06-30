from django.urls import path
from . import views

urlpatterns = [
    path('add/<int:project_id>/', views.add_stakeholder, name='add_stakeholder'),
    path('remove/<int:stakeholder_id>/', views.remove_stakeholder, name='remove_stakeholder'),
]
