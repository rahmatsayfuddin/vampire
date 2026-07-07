from django.urls import path
from . import views

urlpatterns = [
    path('', views.project_list, name='project_list'),
    path('create/', views.project_create, name='project_create'),
    path('create/from_product/<int:product_id>/', views.project_create, name='project_create_from_product'),
    path('update/<int:pk>/', views.project_update, name='project_update'),
    path('delete/<int:pk>/', views.project_delete, name='project_delete'),
    path('<int:pk>/upload-scan/', views.upload_scan, name='upload_scan'),
    path('<int:pk>/scans/compare/', views.compare_scans, name='compare_scans'),
    path('<int:pk>/scan/<int:report_id>/parse/', views.parse_scan, name='parse_scan'),
    path('<int:pk>/scan/<int:sf_id>/promote/', views.promote_scan_finding, name='promote_scan_finding'),
    path('<int:pk>/scan/<int:sf_id>/fp/', views.tag_scan_fp, name='tag_scan_fp'),
    path('scan/<int:report_id>/download/', views.download_scan, name='download_scan'),
    path('scan/<int:report_id>/', views.scan_detail, name='scan_detail'),
    path('scan/<int:report_id>/delete/', views.delete_scan, name='delete_scan'),
    path('<int:pk>/', views.project_detail, name='project_detail'),

    path('sla/', views.sla_profile_list, name='sla_profile_list'),
    path('sla/create/', views.sla_profile_create, name='sla_profile_create'),
    path('sla/<int:pk>/edit/', views.sla_profile_update, name='sla_profile_update'),
    path('sla/<int:pk>/delete/', views.sla_profile_delete, name='sla_profile_delete'),
]
