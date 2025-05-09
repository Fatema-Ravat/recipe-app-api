"""
    Tests for User API
"""

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status

CREATE_USER_URL = reverse('user:create')
TOKEN_URL = reverse('user:token')
ME_URL = reverse('user:me')

def create_user(**params):
    """ create and return new user. """
    return get_user_model().objects.create_user(**params)

class PublicUserApiTests(TestCase):
    """ Tests that feature the user of public user apis """

    def setUp(self):
        self.client = APIClient()

    def test_user_create_success(self):
        """ TEst creating a user successfully """

        payload= {'email': 'test@abc.com',
                  'password':'testpass123',
                  'username': 'test',}
    
        res = self.client.post(CREATE_USER_URL,payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        test_user = get_user_model().objects.get(email=payload['email'])
        #self.assertTrue(test_user.check_password(payload['password']))
        self.assertNotIn('password',res.data)

    def test_user_email_exists_error(self):
        """ Test an error is returned if user with email already exists """

        payload= {'email': 'test@abc.com',
                  'password':'testpass123',
                  'username': 'test',}
        create_user(**payload)
        res = self.client.post(CREATE_USER_URL,payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_user_password_too_short_error(self):
        """ Test an error is returned if the user password is less than 5 chars """

        payload= {'email': 'test@abc.com',
                  'password':'test',
                  'username': 'test',}
        res = self.client.post(CREATE_USER_URL,payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

        user_exists = get_user_model().objects.filter(email = payload['email']).exists()
        self.assertFalse(user_exists)

    def test_create_user_token(self):
        """ Test to create token for valid user """

        user_details = {
            'email':'test@abc.com',
            'password':'test@123',
            'username':'test',
        }
        create_user(**user_details)

        payload = {
            'email': user_details['email'],
            'password': user_details['password'],
        }

        res = self.client.post(TOKEN_URL,payload)

        self.assertEqual(res.status_code,status.HTTP_200_OK)
        self.assertIn('token',res.data)

    def test_create_token_nonvalid_user(self):
        """ Test to create token for non valid user """

        user_details = {
            'email':'test@abc.com',
            'password':'test@123',
            'username':'test',
        }
        create_user(**user_details)

        payload = {
            'email': user_details['email'],
            'password': 'badpassword',
        }

        res = self.client.post(TOKEN_URL,payload)

        self.assertEqual(res.status_code,status.HTTP_400_BAD_REQUEST)

    def test_create_token_blank_password_user(self):
        """ Test to create token for blank password  """

        user_details = {
            'email':'test@abc.com',
            'password':'test@123',
            'username':'test',
        }
        create_user(**user_details)

        payload = {
            'email': user_details['email'],
            'password': '',
        }

        res = self.client.post(TOKEN_URL,payload)

        self.assertEqual(res.status_code,status.HTTP_400_BAD_REQUEST)

    def test_retrive_unauthorized(self):
        """ Test authentication is required for user """
        res = self.client.get(ME_URL)

        self.assertEqual(res.status_code,status.HTTP_401_UNAUTHORIZED)

class PrivateUserAPITests(TestCase):
    """ Tests that require authorization for user """

    def setUp(self):
        """ Initial setup for user for tests """
        self.client = APIClient()

        user_details = {
            'email':'test@abc.com',
            'password':'test@123',
            'username':'test',
        }

        self.user = create_user(**user_details)
        self.client.force_authenticate(user=self.user)
    
    def test_retrieve_user_success(self):
        """ Test the succesfull retrieval of logged in user """

        res = self.client.get(ME_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data,{
            'email':self.user.email,
            'username':self.user.username
        })

    def test_post_me_not_allowed(self):
        """ Test that post is not allowed on the ME url """

        res = self.client.post(ME_URL,{})

        self.assertEqual(res.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_update_user_success(self):
        """ Test that update of username and password for authenticated user """
        
        payload = {'username':'New Username','password':'newpassword123'}
        res = self.client.patch(ME_URL,payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        
        self.user.refresh_from_db()
        self.assertEqual(self.user.username, payload['username'])
