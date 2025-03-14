"""
Tests for models.
"""
from django.test import TestCase
from django.contrib.auth import get_user_model


class ModelTests(TestCase):
    """ Tests for models """

    def test_create_user_with_email(self):
        """ Test for creation of user """

        email = 'test@abc.com'
        password = 'testpass123'

        user = get_user_model().objects.create_user(email=email, password=password)

        self.assertEqual(user.email, email)
        self.assertTrue(user.check_password(password))
    
    def test_check_normalise_email(self):
        """ Test to check if the email address is normalised """

        email_list = [
            ['myemail@ABC.com','myemail@abc.com'],
            ['Myemail@Abc.com','Myemail@abc.com'],
            ['MYEMAIL@ABC.COM', 'MYEMAIL@abc.com'],
        ]

        for email, expected in email_list:
            user = get_user_model().objects.create_user(email=email,password="test123")
            self.assertEqual(user.email, expected)

    def test_email_required(self):
        """ Test for check that email is compulsary """

        with self.assertRaises(ValueError):
            get_user_model().objects.create_user('','test123')
    
    def test_create_superuser(self):
        """ Test for creation of superuser"""

        user = get_user_model().objects.create_superuser("test@abc.com",'test123')

        self.assertTrue(user.is_staff)
        self.assertTrue(user.is_superuser)
