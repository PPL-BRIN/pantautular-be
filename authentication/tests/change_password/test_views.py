from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from django.contrib.auth.hashers import make_password, check_password
from pt_backend.models import User
from unittest.mock import patch, PropertyMock
import os
import jwt
from django.conf import settings

class ChangePasswordViewTest(TestCase):
    
    def setUp(self):
        self.client = APIClient()
        self.url = reverse('change-password')
        
        # Buat user untuk test
        self.user = User.objects.create(
            name="TestUser",
            email="test@example.com",
            password=make_password("current_password"),  # NOSONAR - test data
            role="USER"
        )
        
        # Set up API key authentication
        os.environ['SECRET_API_KEY'] = 'test-api-key'
        self.client.credentials(HTTP_X_API_KEY='test-api-key')
        
        # Create JWT token for the user
        token = jwt.encode(
            {'user_id': str(self.user.id)},
            settings.SECRET_KEY,
            algorithm='HS256'
        )
        self.client.credentials(
            HTTP_X_API_KEY='test-api-key',
            HTTP_AUTHORIZATION=f'Bearer {token}'
        )
    
    def tearDown(self):
        os.environ.pop('SECRET_API_KEY', None)
    
    def test_change_password_success(self):
        # Mock update_user_password untuk mengembalikan success
        with patch('authentication.services.ChangePasswordService.update_user_password') as mock_update:
            mock_update.return_value = {"success": True, "message": "Password successfully updated"}
            
            data = {
                'current_password': 'current_password',  # NOSONAR - test data
                'new_password': 'new_secure_password',  # NOSONAR - test data
                'confirm_password': 'new_secure_password'  # NOSONAR - test data
            }
            
            # Mock serializer is_valid dan validated_data
            with patch('authentication.serializers.ChangePasswordSerializer.is_valid') as mock_is_valid:
                mock_is_valid.return_value = True
                
                with patch('authentication.serializers.ChangePasswordSerializer.validated_data', 
                        new_callable=PropertyMock) as mock_validated_data:
                    mock_validated_data.return_value = {
                        'current_password': 'current_password',
                        'new_password': 'new_secure_password'
                    }
                    
                    response = self.client.post(self.url, data, format='json')
                    
                    # Check response
                    self.assertEqual(response.status_code, status.HTTP_200_OK)
                    self.assertIn('message', response.data)
    
    def test_change_password_incorrect_current(self):
        """Test dengan password saat ini salah"""
        # Mock update_user_password untuk mengembalikan error
        with patch('authentication.services.ChangePasswordService.update_user_password') as mock_update:
            mock_update.return_value = {"success": False, "error": "Current password is incorrect"}
            
            data = {
                'current_password': 'wrong_password',  # NOSONAR - test data
                'new_password': 'new_secure_password',  # NOSONAR - test data
                'confirm_password': 'new_secure_password'  # NOSONAR - test data
            }
            
            # Mock serializer is_valid dan validated_data
            with patch('authentication.serializers.ChangePasswordSerializer.is_valid') as mock_is_valid:
                mock_is_valid.return_value = True
                
                with patch('authentication.serializers.ChangePasswordSerializer.validated_data', 
                        new_callable=PropertyMock) as mock_validated_data:
                    mock_validated_data.return_value = {
                        'current_password': 'wrong_password',
                        'new_password': 'new_secure_password'
                    }
                    
                    response = self.client.post(self.url, data, format='json')
                    
                    # Check response
                    self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
                    self.assertIn('error', response.data)
    
    def test_change_password_no_auth(self):
        """Test tanpa autentikasi"""
        # Remove all credentials
        self.client.credentials()
        
        data = {
            'current_password': 'current_password',  # NOSONAR - test data
            'new_password': 'new_secure_password',  # NOSONAR - test data
            'confirm_password': 'new_secure_password'  # NOSONAR - test data
        }
        
        response = self.client.post(self.url, data, format='json')
        
        # Check response
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_change_password_serializer_error(self):
        """Test ketika serializer mengembalikan error"""
        # Mock serializer is_valid untuk mengembalikan False
        with patch('authentication.serializers.ChangePasswordSerializer.is_valid') as mock_is_valid:
            mock_is_valid.return_value = False
            
            # Mock serializer errors
            with patch('authentication.serializers.ChangePasswordSerializer.errors', 
                    new_callable=PropertyMock) as mock_errors:
                mock_errors.return_value = {"confirm_password": ["Password confirmation does not match."]}
                
                data = {
                    'current_password': 'current_password',  # NOSONAR - test data
                    'new_password': 'new_secure_password',  # NOSONAR - test data
                    'confirm_password': 'different_password'  # NOSONAR - test data
                }
                
                response = self.client.post(self.url, data, format='json')
                
                # Check response
                self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
                self.assertIn('confirm_password', response.data)
    
    def test_change_password_exception(self):
        """Test ketika terjadi exception"""
        with patch('authentication.serializers.ChangePasswordSerializer.is_valid') as mock:
            mock.side_effect = Exception("Test exception")
            
            data = {
                'current_password': 'current_password',  # NOSONAR - test data
                'new_password': 'new_secure_password',  # NOSONAR - test data
                'confirm_password': 'new_secure_password'  # NOSONAR - test data
            }
            
            response = self.client.post(self.url, data, format='json')
            
            # Check response
            self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
            self.assertIn('error', response.data)
    
    def test_missing_authorization_header(self):
        """Test when Authorization header is missing"""
        # Set only API key, remove Authorization header
        self.client.credentials(HTTP_X_API_KEY='test-api-key')
        
        data = {
            'current_password': 'current_password',
            'new_password': 'new_secure_password',
            'confirm_password': 'new_secure_password'
        }
        
        response = self.client.post(self.url, data, format='json')
        
        # Check response
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data['error'], "Authentication token required")

    def test_malformed_authorization_header(self):
        """Test when Authorization header is malformed"""
        # Set malformed Authorization header
        self.client.credentials(
            HTTP_X_API_KEY='test-api-key',
            HTTP_AUTHORIZATION='InvalidFormat token123'
        )
        
        data = {
            'current_password': 'current_password',
            'new_password': 'new_secure_password',
            'confirm_password': 'new_secure_password'
        }
        
        response = self.client.post(self.url, data, format='json')
        
        # Check response
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data['error'], "Authentication token required")

    def test_missing_user_id_in_token(self):
        """Test when token does not contain user_id"""
        # Create token without user_id
        token = jwt.encode(
            {'some_field': 'some_value'},  # No user_id field
            settings.SECRET_KEY,
            algorithm='HS256'
        )
        
        self.client.credentials(
            HTTP_X_API_KEY='test-api-key',
            HTTP_AUTHORIZATION=f'Bearer {token}'
        )
        
        data = {
            'current_password': 'current_password',
            'new_password': 'new_secure_password',
            'confirm_password': 'new_secure_password'
        }
        
        response = self.client.post(self.url, data, format='json')
        
        # Check response
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data['error'], "Invalid token")

    def test_expired_token(self):
        """Test with an expired token"""
        # Use patch to simulate an ExpiredSignatureError
        with patch('jwt.decode') as mock_decode:
            mock_decode.side_effect = jwt.ExpiredSignatureError()
            
            data = {
                'current_password': 'current_password',
                'new_password': 'new_secure_password',
                'confirm_password': 'new_secure_password'
            }
            
            response = self.client.post(self.url, data, format='json')
            
            # Check response
            self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
            self.assertEqual(response.data['error'], "Token expired")

    def test_invalid_token(self):
        """Test with an invalid token"""
        # Use patch to simulate an InvalidTokenError
        with patch('jwt.decode') as mock_decode:
            mock_decode.side_effect = jwt.InvalidTokenError()
            
            data = {
                'current_password': 'current_password',
                'new_password': 'new_secure_password',
                'confirm_password': 'new_secure_password'
            }
            
            response = self.client.post(self.url, data, format='json')
            
            # Check response
            self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
            self.assertEqual(response.data['error'], "Invalid token")

    def test_user_does_not_exist(self):
        """Test when user from token does not exist"""
        # Create token with non-existent user ID
        token = jwt.encode(
            {'user_id': '00000000-0000-0000-0000-000000000000'},  # Non-existent UUID
            settings.SECRET_KEY,
            algorithm='HS256'
        )
        
        self.client.credentials(
            HTTP_X_API_KEY='test-api-key',
            HTTP_AUTHORIZATION=f'Bearer {token}'
        )
        
        data = {
            'current_password': 'current_password',
            'new_password': 'new_secure_password',
            'confirm_password': 'new_secure_password'
        }
        
        # Patch User.objects.get to raise User.DoesNotExist directly
        with patch('pt_backend.models.User.objects.get') as mock_get:
            mock_get.side_effect = User.DoesNotExist("User not found")
            
            response = self.client.post(self.url, data, format='json')
            
            # Check response
            self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
            self.assertEqual(response.data['error'], "User not found")