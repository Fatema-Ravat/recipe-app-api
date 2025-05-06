"""
    Tests for User API
"""

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status

CREATE_USER_URL = reverse('user:create')

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
        self.assertTrue(test_user.check_password(payload['password']))
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
