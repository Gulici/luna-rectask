from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.filters import OrderingFilter
from rest_framework_simplejwt.tokens import RefreshToken
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model
from django_filters.rest_framework import DjangoFilterBackend
from .serializers import UserRegisterSerializer, UserSerializer, HydroponicSystemSerializer, MeasurementSerializer
from .models import HydroponicSystem, Measurement
from .pagination import MeasurementPagination
from .filters import MeasurementFilter, HydroponicSystemFilter


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
    filter_backends = [OrderingFilter, DjangoFilterBackend]
    filterset_class = HydroponicSystemFilter
    ordering_fields = ["name", "created_date"]
    ordering = "created_date"
    
    def get_queryset(self, user):
        """
        Returns a queryset of measurements that belong to a system owned by the authenticated user.
        """
        return HydroponicSystem.objects.filter(owner=user).order_by("created_date")

    # create new system and set authenticated user as owner
    def post(self, request):
        serializer = HydroponicSystemSerializer(
            data=request.data, context={'request': request})
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

        systems = self.get_queryset(user)
        
        filterset = HydroponicSystemFilter(request.GET, queryset=systems)
        if filterset.is_valid():
            systems = filterset.qs
        
        ordering = request.GET.get("ordering", "date_create")
        if ordering.lstrip('-') in self.ordering_fields:
            systems = systems.order_by(ordering)
        
        serializer = HydroponicSystemSerializer(systems, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, pk):
        user = request.user
        system = get_object_or_404(HydroponicSystem, id=pk, owner=user)
        serializer = HydroponicSystemSerializer(
            system, data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, pk):
        user = request.user
        system = get_object_or_404(HydroponicSystem, id=pk, owner=user)
        serializer = HydroponicSystemSerializer(
            system, data=request.data, partial=True, context={'request': request})
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
    """
    API endpoint for managing measurements in a hydroponic system.

    Supported HTTP methods:
    - GET: Retrieve one or all measurements with pagination.
    - POST: Create a new measurement.
    - PUT/PATCH: Update a specific measurement.
    - DELETE: Delete a specific measurement.
    """

    permission_classes = [IsAuthenticated]
    pagination_class = MeasurementPagination
    filter_backends = [OrderingFilter, DjangoFilterBackend]
    filterset_class = MeasurementFilter
    ordering_fields = ['ph', 'temperature', 'tds', 'timestamp']
    ordering = ['timestamp']

    def get_queryset(self, system_id):
        """
        Returns a queryset of measurements that belong to a system owned by the authenticated user.
        """
        return Measurement.objects.filter(
            system__id=system_id, system__owner=self.request.user
        ).order_by('timestamp')

    def get_system(self, system_id):
        """
        Returns the HydroponicSystem if it belongs to the authenticated user, otherwise raises 404.
        """
        return get_object_or_404(HydroponicSystem, id=system_id, owner=self.request.user)

    def get(self, request, system_id, measurement_id=None):
        """
        Retrieve measurements.
        - If `measurement_id` is provided, returns a single measurement.
        - Otherwise, returns a paginated list of all measurements for the system.
        """
        self.get_system(system_id)  # Ensure system belongs to user

        if measurement_id:
            measurement = get_object_or_404(
                self.get_queryset(system_id), id=measurement_id)
            serializer = MeasurementSerializer(measurement)
            return Response(serializer.data, status=status.HTTP_200_OK)
        
        measurements = self.get_queryset(system_id)
        
        filterset = MeasurementFilter(request.GET, queryset=measurements)
        if filterset.is_valid():
            measurements = filterset.qs
        
        ordering = request.GET.get('ordering', 'timestamp')
        if ordering.lstrip('-') in self.ordering_fields:
            measurements = measurements.order_by(ordering)
        
        paginator = self.pagination_class()
        paginated_qs = paginator.paginate_queryset(measurements, request)
        serializer = MeasurementSerializer(paginated_qs, many=True)

        return paginator.get_paginated_response(serializer.data)

    def post(self, request, system_id):
        """
        Create a new measurement in the specified system.
        """
        system = self.get_system(system_id)  # Ensure system belongs to user

        serializer = MeasurementSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(system=system)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, system_id, measurement_id):
        """
        Fully update a specific measurement.
        """
        measurement = get_object_or_404(
            self.get_queryset(system_id), id=measurement_id)
        serializer = MeasurementSerializer(measurement, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, system_id, measurement_id):
        """
        Partially update a specific measurement.
        """
        measurement = get_object_or_404(
            self.get_queryset(system_id), id=measurement_id)
        serializer = MeasurementSerializer(
            measurement, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, system_id, measurement_id):
        """
        Delete a specific measurement.
        """
        measurement = get_object_or_404(
            self.get_queryset(system_id), id=measurement_id)
        measurement.delete()
        return Response({'message': f'Measurement id:{measurement_id} deleted successfully'},
                        status=status.HTTP_204_NO_CONTENT)
