from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import UserRegisterSerializer, UserSerializer, HydroponicSystemSerializer, MeasurementSerializer
from .models import HydroponicSystem, Measurement
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model
import logging

logger = logging.getLogger(__name__)

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
        return Response({'message': f'System id:{pk} deleted succesfully'}, status=status.HTTP_204_NO_CONTENT)
    
    
class MeasurementView(APIView):
    permission_classes = [IsAuthenticated]
    
    # checking that is there system which have specific id and current user is its owner 
    def is_user_and_system_valid(self, request, system_id):
        return HydroponicSystem.objects.filter(id=system_id, owner=request.user).exists()

    def post(self, request, system_id):
        if not self.is_user_and_system_valid(request, system_id):
            return Response({'error': 'No access to this system'}, status=status.HTTP_403_FORBIDDEN)
        
        
        system =  get_object_or_404(HydroponicSystem, id=system_id)
          
        serializer = MeasurementSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(system=system)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
    def get(self, request, system_id, measurement_id=None):
        if not self.is_user_and_system_valid(request, system_id):
            return Response({'error': 'No access to this system'}, status=status.HTTP_403_FORBIDDEN)
        
        system =  get_object_or_404(HydroponicSystem, id=system_id)
        
        if measurement_id:
            measurement = get_object_or_404(Measurement, id=measurement_id)
            serializer = MeasurementSerializer(measurement)
            return Response(serializer.data, status=status.HTTP_200_OK)
        
        measurements = Measurement.objects.filter(system=system)
        serializer = MeasurementSerializer(measurements, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def put(self, request, system_id, measurement_id):
        if not self.is_user_and_system_valid(request, system_id):
            return Response({'error': 'No access to this system'}, status=status.HTTP_403_FORBIDDEN)
        
        measurement = get_object_or_404(Measurement, id=measurement_id)
        serializer = MeasurementSerializer(measurement, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
    def patch(self, request, system_id, measurement_id):
        if not self.is_user_and_system_valid(request, system_id):
            return Response({'error': 'No access to this system'}, status=status.HTTP_403_FORBIDDEN)
        
        measurement = get_object_or_404(Measurement, id=measurement_id)
        serializer = MeasurementSerializer(measurement, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, system_id, measurement_id):
        if not self.is_user_and_system_valid(request, system_id):
            return Response({'error': 'No access to this system'}, status=status.HTTP_403_FORBIDDEN)
        
        measurement = get_object_or_404(Measurement, id=measurement_id)
        measurement.delete()
        return Response({'message': f'Measurement id:{measurement_id} deleted successfully'}, status=status.HTTP_204_NO_CONTENT)
    
    
    
        
