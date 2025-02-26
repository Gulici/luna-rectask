from rest_framework import serializers
from django.contrib.auth import get_user_model
from api.models import HydroponicSystem, Measurement

User = get_user_model()


class UserRegisterSerializer(serializers.ModelSerializer):
    """
    Serializer for user registration.
    Ensures password is write-only and securely hashed during user creation.
    """

    class Meta:
        model = User
        fields = ['id', 'username', 'password']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        """
        Create a new user with a hashed password.
        Uses Django's `create_user()` to automatically handle password hashing.
        """
        return User.objects.create_user(**validated_data)


class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for retrieving basic user information.
    """

    class Meta:
        model = User
        fields = ['id', 'username']


class HydroponicSystemSerializer(serializers.ModelSerializer):
    """
    Serializer for the HydroponicSystem model.
    Ensures `owner` is set automatically during creation.
    """

    class Meta:
        model = HydroponicSystem
        fields = '__all__'
        read_only_fields = ['owner']

    def create(self, validated_data):
        """
        Create a new hydroponic system and set the authenticated user as the owner.
        """
        request = self.context.get('request')
        if request and hasattr(request, "user"):
            validated_data['owner'] = request.user
        return super().create(validated_data)


class MeasurementSerializer(serializers.ModelSerializer):
    """
    Serializer for the Measurement model.
    Ensures `system` and `timestamp` are read-only.
    """

    class Meta:
        model = Measurement
        fields = '__all__'
        read_only_fields = ['system', 'timestamp']
