from rest_framework import serializers
from .models import Project, Task
from django.contrib.auth.models import User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username']


class ProjectSerializer(serializers.ModelSerializer):
    owner = UserSerializer(read_only=True)
    members = UserSerializer(many=True, read_only=True)

    class Meta:
        model = Project
        fields = ['id', 'name', 'description', 'owner', 'members', 'created_at']
        extra_kwargs = {"description": {"required": True}}


class TaskSerializer(serializers.ModelSerializer):
    assignee = serializers.CharField(write_only=True, required=False)  # ورودی username
    project = serializers.IntegerField(write_only=True)  # ورودی ID پروژه

    project_info = serializers.PrimaryKeyRelatedField(read_only=True, source='project')
    assignee_info = UserSerializer(read_only=True, source='assignee')

    class Meta:
        model = Task
        fields = ['id', 'title', 'description', 'status', 'deadline', 'project', 'assignee', 'created_at', 'project_info', 'assignee_info']

    def create(self, validated_data):
        request = self.context['request']
        user = request.user

        project_id = validated_data.pop('project')
        assignee_username = validated_data.pop('assignee', None)

        try:
            project = Project.objects.get(id=project_id, members=user)
        except Project.DoesNotExist:
            raise serializers.ValidationError({'project': 'پروژه معتبر نیست یا شما عضو آن نیستید.'})

        assignee = None
        if assignee_username:
            try:
                assignee = User.objects.get(username=assignee_username)
            except User.DoesNotExist:
                raise serializers.ValidationError({'assignee': 'کاربر مسئول پیدا نشد.'})

        return Task.objects.create(project=project, assignee=assignee, **validated_data)
