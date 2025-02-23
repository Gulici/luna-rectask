from rest_framework.test import APITestCase
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.models import User
from .models import HydroponicSystem
from django.contrib.auth import get_user_model

User = get_user_model()


class HydroponicSystemAPITestCase(APITestCase):

    def setUp(self):
        # Create a test user
        self.user = User.objects.create_user(username='testuser', password='testpass')

        # Authenticate the user
        refresh = RefreshToken.for_user(self.user)
        self.access_token = str(refresh.access_token)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')

        # Create a test hydroponic system
        self.system = HydroponicSystem.objects.create(name="Test System", owner=self.user)

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
    
    # Test retrieving a specific hydroponic system
    def test_get_system_detail(self):
        response = self.client.get(f'{self.url}{self.system.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], self.system.name)
    
    # Test updating a hydroponic system with PUT
    def test_update_system(self):
        name_before = self.system.name
        data = {'name': 'Updated name'}
        response = self.client.put(f'{self.url}{self.system.id}/', data, format='json')
        
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