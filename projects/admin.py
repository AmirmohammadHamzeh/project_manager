from django.contrib import admin
from .models import Project, Task, Comment
admin.site.register(Project)
admin.site.register(Comment)
admin.site.register(Task)