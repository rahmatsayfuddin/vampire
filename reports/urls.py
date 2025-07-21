from django.urls import path
from . import views

urlpatterns = [
    path('generate/<int:project_id>/<str:format>/', views.generate_report, name='generate_report'),
    path('download/<int:report_id>/', views.download_report, name='download_report'),
    path('delete/<int:report_id>/', views.delete_report, name='delete_report'),
]
