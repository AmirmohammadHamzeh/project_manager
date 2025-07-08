from django.urls import path
from .views import ProjectListCreateView, ProjectDetailView, AddMemberView
from .views import TaskListCreateView, TaskDetailView, ProjectTaskListView


urlpatterns = [
    path('projects/', ProjectListCreateView.as_view(), name='project_list_create'),
    path('projects/<int:project_id>/', ProjectDetailView.as_view(), name='project_detail'),
    path('projects/<int:project_id>/add-member/', AddMemberView.as_view(), name='add_project_member'),
    path('tasks/', TaskListCreateView.as_view(), name='task_list_create'),
    path('tasks/<int:pk>/', TaskDetailView.as_view(), name='task_detail'),
    path('projects/<int:project_id>/tasks/', ProjectTaskListView.as_view(), name='project_tasks'),
]