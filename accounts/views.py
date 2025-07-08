from drf_spectacular.utils import extend_schema, OpenApiResponse
from rest_framework.views import APIView
from rest_framework.response import Response
from .serializers import UserSerializer
from rest_framework import status
from rest_framework.permissions import IsAuthenticated


class RegisterView(APIView):
    @extend_schema(
        summary="Register new user",
        description="ثبت‌نام کاربر جدید با دریافت username و password و اطلاعات دیگر از طریق body.",
        request=UserSerializer,
        responses={
            201: OpenApiResponse(description='User successfully created'),
            400: OpenApiResponse(description='Validation error'),
        },
    )
    def post(self, request):
        ser_data = UserSerializer(data=request.data)
        if ser_data.is_valid():
            ser_data.save()
            return Response(data={"message": "User successfully created"}, status=status.HTTP_201_CREATED)
        return Response(ser_data.errors, status=status.HTTP_400_BAD_REQUEST)


class MeView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="Get current user info",
        description="برمی‌گرداند اطلاعات کاربری که با توکن احراز هویت شده.",
        responses={
            200: OpenApiResponse(description='اطلاعات کاربر جاری'),
            401: OpenApiResponse(description='کاربر احراز هویت نشده است'),
        },
    )
    def get(self, request):
        return Response({
            'id': request.user.id,
            'username': request.user.username,
        })
