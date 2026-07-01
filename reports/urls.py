from django.urls import path
from . import views

urlpatterns = [
    path('', views.report_list, name='report_list'),
    path('generate/<int:project_id>/', views.generate_report, name='generate_report'),
    path('download/<int:report_id>/', views.download_report, name='download_report'),
    path('delete/<int:report_id>/', views.delete_report, name='delete_report'),
]
