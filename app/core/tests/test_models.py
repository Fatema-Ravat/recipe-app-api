"""
Tests for models.
"""

from decimal import Decimal
from django.test import TestCase
from django.contrib.auth import get_user_model
from unittest.mock import patch

from core import models

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

    def test_create_recipe(self):
        """ Test to create a new recipe succesfully """

        user = get_user_model().objects.create(email='testuser@example.com',password='testpass123')
        recipe = models.Recipe.objects.create(
            user = user,
            title = 'Test Recipe',
            description = 'Test Recipe desc',
            time_minutes = 10,
            price = Decimal('5.60'),
            calories_per_serving = 100,
        )
        self.assertEqual(str(recipe),recipe.title)

    def test_create_tag(self):
        """ Test to create a new tag successfully """
        user = get_user_model().objects.create(email='testuser@example.com',password='testpass123')
        tag = models.Tag.objects.create(user= user, name ='New Tag')

        self.assertEqual(str(tag),tag.name)

    def test_create_ingredient(self):
        """ test to create a new ingredient successfully """

        user = get_user_model().objects.create(email = 'testuser@example.com', password='passtest123')
        ingredient = models.Ingredient.objects.create(user=user, name = 'Test  Ingredient', )

        self.assertEqual(str(ingredient), ingredient.name)

    @patch('core.models.uuid.uuid4')
    def test_recipe_file_name_uuid(self, mock_uuid):
        """ test to create unique recipe image filename """
        uuid = 'test_path'
        mock_uuid.return_value = uuid
        file_path = models.recipe_image_file_path(None,'example.jpg')

        self.assertEqual(file_path, f'uploads/recipe/{uuid}.jpg')