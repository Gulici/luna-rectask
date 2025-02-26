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
    """
    API endpoint for user registration.
    Allows anyone to register a new account.
    Returns the created user along with JWT tokens.
    """

    permission_classes = [AllowAny]

    def post(self, request):
        """
        Handles user registration.
        - Validates user input.
        - Creates a new user.
        - Returns the user data along with JWT tokens.
        """
        serializer = UserRegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            refresh = RefreshToken.for_user(user)
            return Response(
                {
                    "user": {
                        "id": user.id,
                        "username": user.username,
                    },
                    "refresh": str(refresh),
                    "access": str(refresh.access_token),
                },
                status=status.HTTP_201_CREATED,
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserView(APIView):
    """
    API endpoint for retrieving user data.
    Allows only authenticated users to access user details.
    """

    permission_classes = [IsAuthenticated]

    def get(self, request, user_id=None):
        """
        Retrieves user information.
        - If `user_id` is provided, returns details of a specific user.
        - Otherwise, returns a list of all users.
        """
        if user_id:
            user = get_object_or_404(User, id=user_id)
            serializer = UserSerializer(user)
            return Response(serializer.data, status=status.HTTP_200_OK)

        users = User.objects.all().order_by("username")
        serializer = UserSerializer(users, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    

class HydroponicsSystemView(APIView):
    """
    API endpoint for managing hydroponic systems.
    Supports filtering and sorting. Paginacja is disabled for system lists.
    """

    permission_classes = [IsAuthenticated]
    filter_backends = [OrderingFilter, DjangoFilterBackend]
    filterset_class = HydroponicSystemFilter
    ordering_fields = ["name", "created_date"]
    ordering = "created_date"

    def get_queryset(self, user):
        """
        Returns a queryset of hydroponic systems owned by the authenticated user.
        Uses `order_by()` for default sorting.
        """
        return HydroponicSystem.objects.filter(owner=user).order_by("created_date")

    def post(self, request):
        """
        Creates a new hydroponic system and assigns the authenticated user as the owner.
        """
        serializer = HydroponicSystemSerializer(
            data=request.data, context={'request': request}
        )
        if serializer.is_valid():
            serializer.save(owner=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request, pk=None):
        """
        Retrieves hydroponic systems:
        - If `pk` is provided, returns details of a single system with the last 10 measurements.
        - Otherwise, returns a list of all systems owned by the user.
        """
        user = request.user

        # ✅ Retrieve a single system with eager-loaded measurements
        if pk:
            system = get_object_or_404(
                HydroponicSystem.objects.prefetch_related("measurements"),
                id=pk,
                owner=user,
            )

            last_measurements = list(system.measurements.all().order_by("-timestamp")[:10])

            system_serializer = HydroponicSystemSerializer(system)
            measurement_serializer = MeasurementSerializer(last_measurements, many=True)

            return Response(
                {
                    "system": system_serializer.data,
                    "last_measurements": measurement_serializer.data,
                },
                status=status.HTTP_200_OK,
            )

        # Retrieve multiple systems
        systems = self.get_queryset(user)

        # Filtering
        filterset = HydroponicSystemFilter(request.GET, queryset=systems)
        if not filterset.is_valid():
            return Response(
                {
                    "error": "Invalid filtering parameters",
                    "details": filterset.errors,
                    "valid_filters": list(HydroponicSystemFilter.Meta.fields),
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        systems = filterset.qs

        # Ordering
        ordering = request.GET.get("ordering", "created_date")
        if ordering.lstrip("-") not in self.ordering_fields:
            return Response(
                {
                    "error": f"Invalid ordering field: '{ordering}'",
                    "valid_ordering_fields": self.ordering_fields,
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        systems = systems.order_by(ordering)

        # Serialize and return the list of systems
        serializer = HydroponicSystemSerializer(systems, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, pk):
        """
        Updates an existing hydroponic system.
        The authenticated user must be the owner.
        """
        user = request.user
        system = get_object_or_404(HydroponicSystem, id=pk, owner=user)
        serializer = HydroponicSystemSerializer(
            system, data=request.data, context={'request': request}
        )
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, pk):
        """
        Partially updates an existing hydroponic system.
        The authenticated user must be the owner.
        """
        user = request.user
        system = get_object_or_404(HydroponicSystem, id=pk, owner=user)
        serializer = HydroponicSystemSerializer(
            system, data=request.data, partial=True, context={'request': request}
        )
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        """
        Deletes a hydroponic system.
        The authenticated user must be the owner.
        """
        user = request.user
        system = get_object_or_404(HydroponicSystem, id=pk, owner=user)
        system.delete()
        return Response(
            {"message": f"System id:{pk} deleted successfully"},
            status=status.HTTP_204_NO_CONTENT,
        )


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
