from django.urls import path
from .views import ProjectListCreateView, ProjectDetailView, AddMemberView

urlpatterns = [
    path('projects/', ProjectListCreateView.as_view(), name='project_list_create'),
    path('projects/<int:project_id>/', ProjectDetailView.as_view(), name='project_detail'),
    path('projects/<int:project_id>/add-member/', AddMemberView.as_view(), name='add_project_member'),
]