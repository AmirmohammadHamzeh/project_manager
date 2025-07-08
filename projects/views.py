from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from .models import Project, Task
from .serializers import ProjectSerializer, TaskSerializer
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from drf_spectacular.utils import extend_schema, OpenApiResponse, OpenApiParameter, OpenApiRequest


class ProjectListCreateView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ProjectSerializer

    @extend_schema(
        summary="Create a new project",
        description="این متد یک پروژه‌ی جدید ایجاد می‌کند"
                    " و کاربر جاری را به‌عنوان صاحب و مدیر پروژه و عضو اولیه اضافه می‌کند.",
        request=ProjectSerializer,
        responses={
            201: ProjectSerializer,
            400: OpenApiResponse(description="Bad Request – Invalid input data"),
        },
    )
    def post(self, request):
        ser_data = ProjectSerializer(data=request.data)
        if ser_data.is_valid():
            project = ser_data.save(owner=request.user)
            project.members.add(request.user)
            return Response(ProjectSerializer(project).data, status=status.HTTP_201_CREATED)
        return Response(ser_data.errors, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(
        summary="List all user projects",
        description="لیست تمام پروژه‌هایی که کاربر در آن‌ها عضو است را برمی‌گرداند.",
        responses={
            200: ProjectSerializer(many=True),
        }
    )
    def get(self, request):
        queryset = Project.objects.filter(members=request.user)
        serializer = ProjectSerializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class ProjectDetailView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self, pk, user):
        project = get_object_or_404(Project, pk=pk, members=user)
        return project

    @extend_schema(
        summary="Get a project by ID",
        description="پروژه‌ای را بر اساس شناسه و عضویت کاربر دریافت می‌کند.",
        responses={
            200: ProjectSerializer,
            404: OpenApiResponse(description='پروژه‌ای با این مشخصات پیدا نشد.'),
        }
    )
    def get(self, request, project_id):
        project = self.get_object(project_id, request.user)
        return Response(ProjectSerializer(project).data)

    @extend_schema(
        summary="Update a project",
        description="فقط مالک پروژه می‌تواند آن را ویرایش کند.",
        request=ProjectSerializer,
        responses={
            200: ProjectSerializer,
            403: OpenApiResponse(description='فقط مالک پروژه می‌تواند آن را ویرایش کند.'),
            400: OpenApiResponse(description='درخواست نامعتبر'),
        }
    )
    def put(self, request, project_id):
        project = self.get_object(project_id, request.user)
        if request.user != project.owner:
            return Response({'error': 'فقط مالک پروژه می‌تواند آن را ویرایش کند.'}, status=status.HTTP_403_FORBIDDEN)
        serializer = ProjectSerializer(project, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(
        summary="Delete a project",
        description="فقط مالک پروژه می‌تواند آن را حذف کند.",
        responses={
            204: OpenApiResponse(description='پروژه با موفقیت حذف شد.'),
            403: OpenApiResponse(description='فقط مالک پروژه می‌تواند آن را حذف کند.'),
            404: OpenApiResponse(description='پروژه‌ای با این مشخصات پیدا نشد.'),
        }
    )
    def delete(self, request, project_id):
        project = self.get_object(project_id, request.user)
        if request.user != project.owner:
            return Response({'error': 'فقط مالک پروژه می‌تواند آن را حذف کند.'}, status=status.HTTP_403_FORBIDDEN)
        project.delete()
        return Response({'message': 'project successfully deleted'}, status=status.HTTP_204_NO_CONTENT)


class AddMemberView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(
        summary="Add member to a project",
        description="فقط مالک پروژه می‌تواند با ارسال نام کاربری، یک کاربر را به پروژه اضافه کند.",
        request=OpenApiRequest(
            request={
                'type': 'object',
                'properties': {
                    'username': {'type': 'string', 'example': 'johndoe'}
                },
                'required': ['username']
            }

        ),
        responses={
            200: OpenApiResponse(description='عضو با موفقیت اضافه شد'),
            403: OpenApiResponse(description='فقط مالک پروژه می‌تواند عضو اضافه کند.'),
            404: OpenApiResponse(description='کاربر یا پروژه پیدا نشد.'),
        }
    )
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


class TaskListCreateView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(
        summary="لیست تسک‌های من",
        description="برمی‌گرداند همه‌ی تسک‌هایی که به کاربر جاری تخصیص داده شده‌اند.",
        responses={200: TaskSerializer(many=True)},
    )
    def get(self, request):
        tasks = Task.objects.filter(assignee=request.user)
        serializer = TaskSerializer(tasks, many=True)
        return Response(serializer.data)

    @extend_schema(
        summary="ساخت تسک جدید",
        description="یک تسک جدید می‌سازد و آن را به کاربر جاری یا شخص دیگر اختصاص می‌دهد.",
        request=TaskSerializer,
        responses={
            201: TaskSerializer,
            400: OpenApiResponse(description="خطا در داده‌های ورودی")
        },
    )
    def post(self, request):
        serializer = TaskSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            task = serializer.save()
            return Response(TaskSerializer(task).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class TaskDetailView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self, pk, user):
        task = get_object_or_404(Task, pk=pk)
        if task.project.members.filter(id=user.id).exists():
            return task
        raise PermissionError

    @extend_schema(
        summary="دریافت اطلاعات تسک",
        responses={
            200: TaskSerializer,
            403: OpenApiResponse(description="کاربر مجاز به دیدن این تسک نیست"),
            404: OpenApiResponse(description="تسک پیدا نشد"),
        }
    )
    def get(self, request, pk):
        try:
            task = self.get_object(pk, request.user)
            print(task)
            return Response(TaskSerializer(task).data)
        except PermissionError:
            return Response({'error': 'دسترسی غیرمجاز'}, status=403)

    @extend_schema(
        summary="ویرایش تسک",
        request=TaskSerializer,
        responses={
            200: TaskSerializer,
            400: OpenApiResponse(description="داده‌های نامعتبر"),
            403: OpenApiResponse(description="کاربر مجاز نیست"),
        }
    )
    def put(self, request, pk):
        try:
            task = self.get_object(pk, request.user)
        except PermissionError:
            return Response({'error': 'دسترسی غیرمجاز'}, status=403)

        serializer = TaskSerializer(task, data=request.data, partial=True, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=400)

    @extend_schema(
        summary="حذف تسک",
        responses={
            204: OpenApiResponse(description="تسک با موفقیت حذف شد"),
            403: OpenApiResponse(description="کاربر مجاز به حذف نیست"),
        }
    )
    def delete(self, request, pk):
        try:
            task = self.get_object(pk, request.user)
        except PermissionError:
            return Response({'error': 'دسترسی غیرمجاز'}, status=403)

        task.delete()
        return Response({'message': 'تسک حذف شد'}, status=204)


class ProjectTaskListView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(
        summary="لیست تسک‌های پروژه",
        description="تمام تسک‌های مربوط به یک پروژه خاص را برمی‌گرداند. فقط برای اعضای پروژه.",

        responses={
            200: TaskSerializer(many=True),
            403: OpenApiResponse(description="کاربر عضو پروژه نیست"),
            404: OpenApiResponse(description="پروژه پیدا نشد"),
        }
    )
    def get(self, request, project_id):
        project = get_object_or_404(Project, id=project_id, members=request.user)
        tasks = Task.objects.filter(project=project)
        serializer = TaskSerializer(tasks, many=True)
        return Response(serializer.data)
