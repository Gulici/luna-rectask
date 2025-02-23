from django.contrib.auth import authenticate
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import generics
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import UserRegisterSerializer, UserSerializer, HydroponicSystemSerializer
from .models import HydroponicSystem
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model

User = get_user_model()


class RegisterView(APIView):
    permission_classes = [AllowAny]
    
    def post(self, request):
        serializer = UserRegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            refresh = RefreshToken.for_user(user)
            return Response({
                'user': {
                    'id': user.id,
                    'username': user.username,
                },
                'refresh': str(refresh),
                'access': str(refresh.access_token),
                }, 
                status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    
class UserView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request, user_id=None):
        if user_id:
            user = get_object_or_404(User, id=user_id)
            serializer = UserSerializer(user)
            return Response(serializer.data, status=status.HTTP_200_OK)
        
        users = User.objects.all()
        serializer = UserSerializer(users, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    

class HydroponicsSystemView(APIView):
    permission_classes = [IsAuthenticated]
    
    #create new system and set authenticated user as owner
    def post(self, request):
        serializer = HydroponicSystemSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save(owner=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def get(self, request, pk=None):
        user = request.user
        if pk:
            system = get_object_or_404(HydroponicSystem, id=pk, owner=user)
            serializer = HydroponicSystemSerializer(system)
            return Response(serializer.data, status=status.HTTP_200_OK)
        
        systems = user.systems.all()
        serializer = HydroponicSystemSerializer(systems, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def put(self, request, pk):
        user = request.user
        system = get_object_or_404(HydroponicSystem, id=pk, owner=user)
        serializer = HydroponicSystemSerializer(system, data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, pk):
        user = request.user
        system = get_object_or_404(HydroponicSystem, id=pk, owner=user)
        serializer = HydroponicSystemSerializer(system, data=request.data, partial=True, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, requset, pk):
        user = requset.user
        system = get_object_or_404(HydroponicSystem, id=pk, owner=user)
        system.delete()
        return Response({'message': 'System id:{pk} deleted succesfully'}, status=status.HTTP_204_NO_CONTENT)