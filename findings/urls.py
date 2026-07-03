from django.urls import path
from . import views

urlpatterns = [
    path('', views.finding_list, name='finding_list'),
    path('create/<int:project_id>/', views.create_finding, name='create_finding'),
    path('<int:pk>/', views.finding_detail, name='finding_detail'),
    path('<int:pk>/edit/', views.edit_finding, name='finding_edit'),
    path('<int:pk>/comment/', views.add_comment, name='add_comment'),
    path('<int:pk>/accept-risk/', views.accept_risk, name='accept_risk'),
    path('<int:pk>/delete/', views.delete_finding, name='finding_delete'),
    path('upload-poc-image/', views.upload_poc_image, name='upload_poc_image'),
]
