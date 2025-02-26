from rest_framework.test import APITestCase
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model
from .models import HydroponicSystem, Measurement

User = get_user_model()


class HydroponicSystemAPITestCase(APITestCase):

    def setUp(self):
        # Create a test user
        self.user = User.objects.create_user(
            username='testuser', password='testpass')

        # Authenticate the user
        refresh = RefreshToken.for_user(self.user)
        self.access_token = str(refresh.access_token)
        self.client.credentials(
            HTTP_AUTHORIZATION=f'Bearer {self.access_token}')

        # Create a test hydroponic system
        self.system = HydroponicSystem.objects.create(
            name="Test System", owner=self.user)

        # API endpoint
        self.url = "/api/systems/"

    # Test creating new system by authorized user
    def test_create_system(self):
        data_list = [{'name': 'new system'}, {'name': 'another system'}]

        response1 = self.client.post(self.url, data_list[0], format='json')
        self.assertEqual(response1.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response1.data['name'], 'new system')
        self.assertEqual(response1.data['owner'], self.user.id)

        response2 = self.client.post(self.url, data_list[1], format='json')
        self.assertEqual(response2.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response2.data['name'], 'another system')
        self.assertEqual(response2.data['owner'], self.user.id)

    # Test retrieving all hydroponic systems of user
    def test_get_system_list(self):
        HydroponicSystem.objects.create(name='System 1', owner=self.user)
        HydroponicSystem.objects.create(name='System 2', owner=self.user)

        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 3)
        
    def test_get_ordered_systems_list(self):
        HydroponicSystem.objects.create(name='System 1', owner=self.user)
        HydroponicSystem.objects.create(name='System 2', owner=self.user)
        
        response = self.client.get(f"{self.url}?ordering=-date_create")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data[0]["name"], "Test System")
        self.assertEqual(response.data[2]["name"], "System 2")
        
    def test_get_sorted_systems_list(self):
        HydroponicSystem.objects.create(name='System 1', owner=self.user)
        HydroponicSystem.objects.create(name='System 2', owner=self.user)
        
        response = self.client.get(f"{self.url}?date_before=2025-12-31&date_after=2024-05-05")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertNotEqual(len(response.data), 0)

    # Test retrieving a specific hydroponic system
    def test_get_system_detail(self):
        response = self.client.get(f'{self.url}{self.system.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], self.system.name)

    # Test updating a hydroponic system with PUT
    def test_update_system(self):
        name_before = self.system.name
        data = {'name': 'Updated name'}
        response = self.client.put(
            f'{self.url}{self.system.id}/', data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertNotEqual(response.data['name'], name_before)
        self.assertEqual(response.data['name'], 'Updated name')

    # Test deleting a hydroponic system
    def test_delete_system(self):
        response_del = self.client.delete(f'{self.url}{self.system.id}/')
        response_get_list = self.client.get(self.url)

        self.assertEqual(response_del.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(response_get_list.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response_get_list.data), 0)

    # Test unautorized user cannot create a system
    def test_unauthorized_user_create_system(self):
        self.client.credentials()
        data = {'name': 'unauthorized'}
        response = self.client.post(self.url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class MeasurementAPITestCase(APITestCase):
    """
    Test case for API endpoints related to measurement management in hydroponic systems.
    """

    def setUp(self):
        """
        Prepares test data:
        - Creates a user and authenticates them.
        - Creates a hydroponic system for the user.
        - Creates an initial measurement.
        - Stores API URLs for easy access.
        """
        self.user = User.objects.create_user(
            username="testuser", password="testpass")

        # Authenticate the user
        refresh = RefreshToken.for_user(self.user)
        self.access_token = str(refresh.access_token)
        self.client.credentials(
            HTTP_AUTHORIZATION=f"Bearer {self.access_token}")

        # Create a hydroponic system
        self.system = HydroponicSystem.objects.create(
            name="Test System", owner=self.user)

        # Create a test measurement
        self.measurement = Measurement.objects.create(
            system=self.system, ph=6.5, temperature=22.3, tds=800)

        # API URLs
        self.m_url = f"/api/systems/{self.system.id}/measurements/"
        self.m_det_url = f"/api/systems/{self.system.id}/measurements/{self.measurement.id}/"

    def test_create_measurement(self):
        """
        Test creating a new measurement.
        """
        data = {"ph": 7.0, "temperature": 24.0, "tds": 850}
        response = self.client.post(self.m_url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["ph"], 7.0)
        self.assertEqual(response.data["temperature"], 24.0)
        self.assertEqual(response.data["tds"], 850)
        self.assertEqual(response.data["system"], self.system.id)

    def test_get_measurement_list(self):
        """
        Test retrieving a paginated list of measurements for a specific system.
        """
        Measurement.objects.create(
            system=self.system, ph=6.8, temperature=23.5, tds=780)
        Measurement.objects.create(
            system=self.system, ph=6.2, temperature=21.0, tds=820)

        response = self.client.get(self.m_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 3)

    def test_get_measurement_ordered_list(self):
        """
        Test retrieving a list of measurements ordered by pH.
        """
        Measurement.objects.create(
            system=self.system, ph=6.8, temperature=23.5, tds=780)
        Measurement.objects.create(
            system=self.system, ph=6.2, temperature=21.0, tds=820)

        response = self.client.get(f"{self.m_url}?ordering=ph")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 3)
        self.assertEqual(response.data["results"][0]["ph"], 6.2)

    def test_get_measurement_sorted_list(self):
        """
        Test filtering and sorting of measurements using query parameters.
        """
        Measurement.objects.create(
            system=self.system, ph=6.8, temperature=23.5, tds=780)
        Measurement.objects.create(
            system=self.system, ph=6.2, temperature=21.0, tds=820)

        test_cases = [
            {"query": "?ordering=-temperature&ph_min=6.3&ph_max=8.1",
                "expected_length": 2, "expected_first_temp": 23.5},
            {"query": "?timestamp_before=2024-12-31", "expected_length": 0},
            {"query": "?temperature_min=23.0", "expected_length": 1},
            {"query": "?tds_max=800", "expected_length": 2},
        ]

        for case in test_cases:
            with self.subTest(query=case["query"]):
                response = self.client.get(f"{self.m_url}{case['query']}")
                self.assertEqual(response.status_code, status.HTTP_200_OK)
                self.assertEqual(
                    len(response.data["results"]), case["expected_length"])

                if "expected_first_temp" in case:
                    self.assertEqual(
                        response.data["results"][0]["temperature"], case["expected_first_temp"])

    def test_get_measurement_detail(self):
        """
        Test retrieving a specific measurement by its ID.
        """
        response = self.client.get(self.m_det_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["ph"], self.measurement.ph)
        self.assertEqual(response.data["temperature"],
                         self.measurement.temperature)
        self.assertEqual(response.data["tds"], self.measurement.tds)

    def test_update_measurement(self):
        """
        Test updating an existing measurement using PUT.
        """
        data = {"ph": 7.2, "temperature": 25.0, "tds": 900}
        response = self.client.put(self.m_det_url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["ph"], 7.2)
        self.assertEqual(response.data["temperature"], 25.0)
        self.assertEqual(response.data["tds"], 900)

    def test_partial_update_measurement(self):
        """
        Test partially updating a measurement using PATCH.
        """
        data = {"ph": 6.9}
        response = self.client.patch(self.m_det_url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["ph"], 6.9)
        self.assertEqual(response.data["temperature"],
                         self.measurement.temperature)

    def test_delete_measurement(self):
        """
        Test deleting a measurement.
        """
        # Ensure measurement exists before deletion
        self.assertTrue(Measurement.objects.filter(
            id=self.measurement.id).exists())

        response_del = self.client.delete(self.m_det_url)
        response_get = self.client.get(self.m_det_url)

        # Verify measurement was deleted
        self.assertEqual(response_del.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(response_get.status_code, status.HTTP_404_NOT_FOUND)

    def test_unauthorized_user_create_measurement(self):
        """
        Test that an unauthorized user cannot create a measurement.
        """
        self.client.credentials()  # Disable authentication
        data = {"ph": 7.1, "temperature": 23.0, "tds": 870}
        response = self.client.post(self.m_url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_user_cannot_edit_other_user_measurement(self):
        """
        Test that a user cannot edit a measurement from another user's system.
        """
        other_user = User.objects.create_user(
            username="otheruser", password="testpass")
        other_system = HydroponicSystem.objects.create(
            name="Other System", owner=other_user)
        other_measurement = Measurement.objects.create(
            system=other_system, ph=6.0, temperature=20.0, tds=750)

        # Attempt to edit another user's measurement
        other_measurement_url = f"/api/systems/{other_system.id}/measurements/{other_measurement.id}/"
        data = {"ph": 7.0}
        response = self.client.patch(
            other_measurement_url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
