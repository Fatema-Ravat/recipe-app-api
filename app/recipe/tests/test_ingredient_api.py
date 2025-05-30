""" Test for Ingredients of Recipe """

from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Ingredient
from recipe.serializers import IngredientSerializer

INGREDIENTS_URL = reverse('recipe:ingredient-list')

def get_detail_url(ingredient_id):
    """ create Ingredient detail url """
    return reverse('recipe:ingredient-detail', args=[ingredient_id])

def create_user(email='test@abc.com', password='testpass123'):
    """ create user function """
    return get_user_model().objects.create_user(email=email,password=password)

class PublicIngredientAPITest(TestCase):
    """ Test for unauthenticated Ingredients API request"""

    def setUp(self):
        self.client = APIClient()
    
    def test_auth_required(self):
        """ Test that unauthorized user cannot list tags """
        res = self.client.get(INGREDIENTS_URL)
        
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

class PrivateIngredientAPITest(TestCase):
    """ Test for authenticated Ingredients API request """

    def setUp(self):
        self.client = APIClient()
        self.user = create_user()
        
        self.client.force_authenticate(self.user)

    def test_ingredient_list(self):
        """ test for listing of ingredient """

        Ingredient.objects.create(user=self.user , name ='Ing1')
        Ingredient.objects.create(user=self.user, name='Ing2')

        res = self.client.get(INGREDIENTS_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        ing = Ingredient.objects.all().order_by('-name')
        serializer = IngredientSerializer(ing, many = True)

        self.assertEqual(res.data, serializer.data)

    def test_ingredient_list_for_authorized_user(self):
        """ test for listing of ingredient for authorized user only """

        new_user = create_user(email='test2@example.com')
        ing1 = Ingredient.objects.create(user=self.user , name ='Ing1')
        Ingredient.objects.create(user=new_user, name='Ing2')

        res = self.client.get(INGREDIENTS_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        self.assertEqual(len(res.data),1)

        ing = Ingredient.objects.filter(user=self.user).order_by('-name')
        serializer = IngredientSerializer(ing, many = True)

        self.assertEqual(res.data, serializer.data)

    def test_update_ingredient_api(self):
        """ test to update ingredient """

        ing1 = Ingredient.objects.create(user = self.user, name = 'Chilli')

        detail_url = get_detail_url(ing1.id)
        payload = {'name': 'Mirchi'}

        res = self.client.patch(detail_url, payload)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        ing1.refresh_from_db()

        self.assertEqual(ing1.name,payload['name'])


    def test_delete_ingredient_api(self):
        """ test to delete an ingredient """
        ing = Ingredient.objects.create(user=self.user, name = 'TobeDeleted')

        detail_url= get_detail_url(ing.id)
        res = self.client.delete(detail_url)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Ingredient.objects.filter(id=ing.id).exists())
