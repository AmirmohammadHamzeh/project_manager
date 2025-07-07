from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from .models import Project
from .serializers import ProjectSerializer
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404


class ProjectListCreateView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        ser_data = ProjectSerializer(data=request.data)
        if ser_data.is_valid():
            project = ser_data.save(owner=request.user)
            project.members.add(request.user)
            return Response(ProjectSerializer(project).data, status=status.HTTP_201_CREATED)
        return Response(ser_data.errors, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request):
        queryset = Project.objects.filter(members=request.user)
        serializer = ProjectSerializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class ProjectDetailView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self, pk, user):
        project = get_object_or_404(Project, pk=pk, members=user)
        return project

    def get(self, request, project_id):
        project = self.get_object(project_id, request.user)
        return Response(ProjectSerializer(project).data)

    def put(self, request, project_id):
        project = self.get_object(project_id, request.user)
        if request.user != project.owner:
            return Response({'error': 'فقط مالک پروژه می‌تواند آن را ویرایش کند.'}, status=status.HTTP_403_FORBIDDEN)
        serializer = ProjectSerializer(project, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, project_id):
        project = self.get_object(project_id, request.user)
        if request.user != project.owner:
            return Response({'error': 'فقط مالک پروژه می‌تواند آن را حذف کند.'}, status=status.HTTP_403_FORBIDDEN)
        project.delete()
        return Response({'message': 'project successfully deleted'}, status=status.HTTP_204_NO_CONTENT)


class AddMemberView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, project_id):
        project = get_object_or_404(Project, pk=project_id)
        if request.user != project.owner:
            return Response({'error': 'فقط مالک پروژه می‌تواند عضو اضافه کند.'}, status=403)

        username = request.data.get('username')
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            return Response({'error': 'کاربر پیدا نشد.'}, status=404)

        project.members.add(user)
        return Response({'message': f'کاربر {username} با موفقیت اضافه شد ✅'})
