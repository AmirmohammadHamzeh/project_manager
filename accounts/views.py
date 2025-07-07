from rest_framework.views import APIView
from rest_framework.response import Response
from .serializers import UserSerializer
from rest_framework import status
from rest_framework.permissions import IsAuthenticated


class RegisterView(APIView):
    def post(self, request):
        ser_data = UserSerializer(data=request.data)  # ← این بهتر از request.POST هست
        if ser_data.is_valid():
            ser_data.save()  # ← از متد create داخل Serializer استفاده می‌کنه
            return Response(data={"message": "User successfully created"}, status=status.HTTP_201_CREATED)
        return Response(ser_data.errors, status=status.HTTP_400_BAD_REQUEST)


class MeView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response({
            'id': request.user.id,
            'username': request.user.username,
        })
