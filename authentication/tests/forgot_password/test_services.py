from django.test import TestCase
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.utils.encoding import force_bytes
from unittest.mock import patch, MagicMock
from authentication.services import PasswordResetService
from django.contrib.auth.tokens import default_token_generator
from pt_backend.models import User

from sib_api_v3_sdk.rest import ApiException

class TestPasswordResetService(TestCase):
    def setUp(self):
        self.user = User.objects.create(
            email='test@example.com',
            name='testuser',
            password='oldpassword123',
            role="TEST ROLE"
        )
        self.service = PasswordResetService()
        
    def test_find_user_by_email_successful(self):
        """Test that a user can be found by email"""
        user = self.service.find_user_by_email('test@example.com')
        self.assertEqual(user.name, 'testuser')
        
    def test_generate_token_successful(self):
        """Test that token generation produces valid uid and token"""
        uid, token = self.service.generate_password_reset_token(self.user)
        # Verify uid decodes to the user's id
        decoded_uid = urlsafe_base64_decode(uid).decode()
        self.assertEqual(int(decoded_uid), self.user.id)
        # Token should be a non-empty string
        self.assertTrue(token and isinstance(token, str))
        
    def test_create_reset_link_successful(self):
        """Test that reset link creation works properly"""
        uid, token = self.service.generate_password_reset_token(self.user)
        link = self.service.create_password_reset_link(uid, token)
        
        self.assertTrue(link.startswith("http://localhost:3000/forgot-password/reset"))
        
        self.assertTrue(f"?uid={uid}" in link)
        self.assertTrue(f"&token={token}" in link)
        
        expected_format = f"{self.service.reset_url_base}?uid={uid}&token={token}"
        self.assertEqual(link, expected_format)
        
    @patch('authentication.services.send_mail')
    def test_send_reset_email_successful(self, mock_send_mail):
        """Test that email sending works properly"""
        self.service.send_password_reset_email('test@example.com', 'https://test.link')
        mock_send_mail.assert_called_once()
    
    def test_find_nonexistent_user(self):
        """Test finding a user that doesn't exist"""
        user = self.service.find_user_by_email('nonexistent@example.com')
        self.assertIsNone(user)
        
    @patch('authentication.services.PasswordResetService.send_password_reset_email')
    def test_process_reset_nonexistent_user(self, mock_send_email):
        """Test processing reset with non-existent user"""
        with self.assertRaises(AttributeError): 
            self.service.process_reset_request('nonexistent@example.com')
        
    @patch('authentication.services.send_mail')
    def test_send_email_error(self, mock_send_mail):
        """Test handling email sending error"""
        mock_send_mail.side_effect = Exception("Email error")
        with self.assertRaises(Exception):
            self.service.send_password_reset_email('test@example.com', 'https://test.link')
            
    def test_generate_token_invalid_user(self):
        """Test token generation with invalid user"""
        invalid_user = MagicMock()
        invalid_user.pk = None
        with self.assertRaises(Exception):
            self.service.generate_password_reset_token(invalid_user)
    
    def test_empty_email(self):
        """Test handling empty email"""
        user = self.service.find_user_by_email('')
        self.assertIsNone(user)
        
    @patch('authentication.services.send_mail')
    def test_unicode_email(self, mock_send_mail):
        """Test handling email with unicode characters"""
        User.objects.create(
            email='tëst@exämple.com',
            name='unicodeuser',
            password='password123',
            role="TEST ROLE"
        )
        
        self.service.send_password_reset_email('tëst@exämple.com', 'https://test.link')
        mock_send_mail.assert_called_once()
        
    def test_special_chars_in_url(self):
        """Test handling special characters in URL base"""
        service = PasswordResetService(reset_url_base="http://localhost:3000/authentication/reset-password?special=!@#$%^&*()")
        uid, token = service.generate_password_reset_token(self.user)
        link = service.create_password_reset_link(uid, token)
        self.assertTrue('!@#$%^&*()' in link)
    
    def test_get_user_from_uidb64_valid(self):
        """Test retrieving a user from a valid uidb64"""
        uidb64 = urlsafe_base64_encode(force_bytes(self.user.pk))
        user = self.service.get_user_from_uidb64(uidb64)
        self.assertEqual(user.id, self.user.id)
        self.assertEqual(user.email, 'test@example.com')

    def test_get_user_from_uidb64_invalid_format(self):
        """Test retrieving a user with invalid uidb64 format"""
        user = self.service.get_user_from_uidb64('invalid-base64')
        self.assertIsNone(user)

    def test_get_user_from_uidb64_nonexistent_user(self):
        """Test retrieving a non-existent user from uidb64"""
        uidb64 = urlsafe_base64_encode(force_bytes(99999))
        user = self.service.get_user_from_uidb64(uidb64)
        self.assertIsNone(user)

    def test_get_user_from_uidb64_empty(self):
        """Test retrieving a user with empty uidb64"""
        user = self.service.get_user_from_uidb64('')
        self.assertIsNone(user)

    def test_validate_token_valid(self):
        """Test validating a valid token"""
        token = default_token_generator.make_token(self.user)
        result = self.service.validate_token(self.user, token)
        self.assertTrue(result)

    def test_validate_token_invalid(self):
        """Test validating an invalid token"""
        token = "invalid-token"
        result = self.service.validate_token(self.user, token)
        self.assertFalse(result)

    def test_validate_token_none_user(self):
        """Test validating a token with None user"""
        token = "some-token"
        result = self.service.validate_token(None, token)
        self.assertFalse(result)

    def test_validate_token_empty(self):
        """Test validating an empty token"""
        token = ""
        result = self.service.validate_token(self.user, token)
        self.assertFalse(result)

    @patch('authentication.services.TransactionalEmailsApi')
    @patch('authentication.services.ApiClient')
    @patch('authentication.services.os.getenv')
    def test_send_brevo_email_successful(self, mock_getenv, mock_api_client, mock_transactional_api):
        """Test successful sending of email via Brevo"""
        mock_getenv.return_value = "mock-api-key"
        mock_api_instance = mock_transactional_api.return_value
        mock_api_instance.send_transac_email.return_value = {"message_id": "test-id"}
        
        reset_link = "https://example.com/reset/abc123/def456"
        email = "user@example.com"
        self.service.send_brevo_email(reset_link, email)
        
        mock_api_instance.send_transac_email.assert_called_once()
        
        send_email_call = mock_api_instance.send_transac_email.call_args[0][0]
        self.assertEqual(send_email_call.to[0]["email"], email)
        self.assertEqual(send_email_call.sender["name"], "PPL BRIN")
        self.assertEqual(send_email_call.template_id, 1)  # Default template_id
        self.assertEqual(send_email_call.params["reset_link"], reset_link)

    @patch('authentication.services.TransactionalEmailsApi')
    @patch('authentication.services.ApiClient')
    @patch('authentication.services.os.getenv')
    def test_send_brevo_email_custom_template(self, mock_getenv, mock_api_client, mock_transactional_api):
        """Test sending email with custom template ID"""
        mock_getenv.return_value = "mock-api-key"
        mock_api_instance = mock_transactional_api.return_value
        
        custom_template_id = 5
        self.service.send_brevo_email("https://example.com/reset", "user@example.com", custom_template_id)
        
        send_email_call = mock_api_instance.send_transac_email.call_args[0][0]
        self.assertEqual(send_email_call.template_id, custom_template_id)

    @patch('authentication.services.TransactionalEmailsApi')
    @patch('authentication.services.ApiClient')
    @patch('authentication.services.os.getenv')
    @patch('builtins.print')
    def test_send_brevo_email_api_exception(self, mock_print, mock_getenv, mock_api_client, mock_transactional_api):
        """Test handling of API exception when sending email"""
        mock_getenv.return_value = "mock-api-key"
        mock_api_instance = mock_transactional_api.return_value
        mock_api_instance.send_transac_email.side_effect = ApiException(reason="API Error")
        
        self.service.send_brevo_email("https://example.com/reset", "user@example.com")
        
        mock_print.assert_any_call("Exception when calling TransactionalEmailsApi->send_transac_email: %s\n" % mock_api_instance.send_transac_email.side_effect)

    @patch('authentication.services.TransactionalEmailsApi')
    @patch('authentication.services.ApiClient')
    @patch('authentication.services.os.getenv')
    def test_send_brevo_email_missing_api_key(self, mock_getenv, mock_api_client, mock_transactional_api):
        """Test behavior when API key is missing"""
        mock_getenv.return_value = None
        
        self.service.send_brevo_email("https://example.com/reset", "user@example.com")
        
        mock_api_client.assert_called_once()
        config = mock_api_client.call_args[0][0]
        self.assertIsNone(config.api_key.get('api-key'))

    @patch('authentication.services.PasswordResetService.send_brevo_email')
    def test_process_reset_request_uses_brevo(self, mock_send_brevo):
        """Test that process_reset_request uses send_brevo_email"""
        mock_send_brevo.return_value = None
        
        self.service.process_reset_request('test@example.com')
        
        mock_send_brevo.assert_called_once()
        args = mock_send_brevo.call_args[0]
        self.assertTrue(len(args) >= 2) 
        self.assertEqual(args[1], 'test@example.com')  

    @patch('authentication.services.TransactionalEmailsApi')
    @patch('authentication.services.ApiClient')
    @patch('authentication.services.os.getenv')
    def test_send_brevo_email_special_chars(self, mock_getenv, mock_api_client, mock_transactional_api):
        """Test sending email with special characters in reset link"""
        mock_getenv.return_value = "mock-api-key"
        mock_api_instance = mock_transactional_api.return_value
        
        special_link = "https://example.com/reset?token=abc&id=123#section"
        self.service.send_brevo_email(special_link, "user@example.com")
        
        send_email_call = mock_api_instance.send_transac_email.call_args[0][0]
        self.assertEqual(send_email_call.params["reset_link"], special_link)