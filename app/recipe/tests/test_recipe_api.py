""" Tests to test the recipe app apis """

from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Recipe, Tag
from recipe.serializers import RecipeSerializer, RecipeDetailSerializer

RECIPES_URL = reverse('recipe:recipe-list')

def create_detial_url(recipe_id):
    """ fucntion to create recipe detail url """
    detail_url = reverse('recipe:recipe-detail',args=[recipe_id])
    return detail_url

def create_recipe(user, **params):
    """ create a recipe for authorized user"""
    defaults = {
        'title':'Sample recipe',
        'description':'Sample Description',
        'time_minutes':15,
        'price': Decimal('300.20'),
        'link': 'http://example.com/sample-recipe.pdf',
    }
    defaults.update(params)

    recipe = Recipe.objects.create(user=user, **defaults)
    return recipe

def create_user(**params):
    """ create a new user """
    return get_user_model().objects.create_user(**params)


class PublicRecipeAPITests(TestCase):
    """ Test for Recipe api for unauthorized user """

    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        """ Test that authorization required for recipe urls """
        res = self.client.get(RECIPES_URL)

        self.assertEqual(res.status_code,status.HTTP_401_UNAUTHORIZED)

class PrivateRecipeAPITests(TestCase):
    """ Test for Recipe api for authorized user """

    def setUp(self):
        self.client = APIClient()
        self.user = create_user(email='testemail@abc.com',password='testpass123')

        self.client.force_authenticate(self.user)

    def test_retrieve_recipes(self):
        """ Test to retrieve list of recipes """
        create_recipe(self.user)
        create_recipe(self.user)

        res= self.client.get(RECIPES_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)

        recipes = Recipe.objects.all().order_by('-id')
        recipe_serializer = RecipeSerializer(recipes,many=True)

        self.assertEqual(res.data,recipe_serializer.data)

    def test_retrieve_recipes_only_authorized_user(self):
        """ Test to retreive list of receipe for authorized users """

        new_user = create_user(email='testuser2@abc.com',password='passtest12143')
        create_recipe(user=new_user)
        create_recipe(user=self.user)

        res= self.client.get(RECIPES_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)

        recipes = Recipe.objects.filter(user=self.user).order_by('-id')
        recipe_serializer = RecipeSerializer(recipes,many=True)

        self.assertEqual(res.data,recipe_serializer.data)

    def test_retrieve_recipe_detail(self):
        """ test for retrieving a specific recipe API """

        my_recipe = create_recipe(user = self.user)
        recipe_detail_url = create_detial_url(my_recipe.id)

        res = self.client.get(recipe_detail_url)

        self.assertEqual(res.status_code, status.HTTP_200_OK)

        recipe_serializer = RecipeDetailSerializer(my_recipe)
        self.assertEqual(res.data,recipe_serializer.data)

    def test_create_recipe(self):
        """ test to create a recipe """

        payload = {
            'title':'Sample recipe',
            'description':'Sample Description',
            'time_minutes':15,
            'price': Decimal('300.20')
        }
        res = self.client.post(RECIPES_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        recipe = Recipe.objects.get(id = res.data['id'])

        for k, v in payload.items():
            self.assertEqual(getattr(recipe,k),v)
            # in the above code as the attribute (k) value of recipe is dynamic
            # we cannot directly use recipe.title, so function getattr(object,attribute) used.

        self.assertEqual(recipe.user,self.user)

    def test_partial_update(self):
        """ test to partial update of recipe """

        original_link = 'https://example.com/original_link.pdf'
        recipe = create_recipe(user=self.user,title='New recipe title',link=original_link)

        detail_url = create_detial_url(recipe.id)

        payload ={'title':'Updated recipe title'}

        res= self.client.patch(detail_url, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        recipe.refresh_from_db()

        self.assertEqual(self.user,recipe.user)
        self.assertEqual(recipe.title,payload['title'])
    
    def test_full_update(self):
        """ test full update of recipe """

        recipe = create_recipe(user=self.user, title='New recipe',description='Recipe desc')

        detail_url=create_detial_url(recipe.id)

        payload= {
            'title':'Updated title',
            'time_minutes':30,
            'price': Decimal('400'),
            'link': 'http://example.com/new_sample-recipe.pdf'
        }

        res= self.client.put(detail_url,payload)
        self.assertEqual(res.status_code,status.HTTP_200_OK)
        recipe.refresh_from_db()

        self.assertEqual(self.user,recipe.user)
        for k,v in payload.items():
            self.assertEqual(getattr(recipe,k), v)

    def test_user_update_returns_error(self):
        """ test to check that updating user returns error"""

        recipe= create_recipe(user=self.user)
        new_user= create_user(email='newuser@abc.com',password ='newtestpass@123')

        payload={
            'user':new_user.id
        }
        detail_url = create_detial_url(recipe.id)

        res= self.client.patch(detail_url,payload)
        recipe.refresh_from_db()

        self.assertEqual(recipe.user,self.user)
        # as status code will return error not checking that, just checking that user is not updated

    def test_delete_recipe(self):
        """ test for deleting recipe """

        recipe = create_recipe(user= self.user)
        detail_url = create_detial_url(recipe.id)

        res= self.client.delete(detail_url)
        self.assertEqual(res.status_code,status.HTTP_204_NO_CONTENT)
        self.assertFalse(Recipe.objects.filter(id=recipe.id).exists())

    def test_not_delete_other_user_recipe(self):
        """ test that it does not allow to delete other user recipe """
        new_user= create_user(email='newuser@abc.com',password ='newtestpass@123')
        recipe = create_recipe(user=new_user)

        detail_url = create_detial_url(recipe.id)
        res = self.client.delete(detail_url)

        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)
        self.assertTrue(Recipe.objects.filter(id=recipe.id).exists())

    def test_create_recipe_with_new_tags(self):
        """ test to create recipe with new tags """

        payload = {
            'title': 'Thai Chicken Curry',
            'time_minutes': 30,
            'price': Decimal('350'),
            'tags' : [{'name': 'Thai'},{'name':'Dinner'}],
        }

        res = self.client.post(RECIPES_URL,payload,format='json')
        self.assertEqual(res.status_code,status.HTTP_201_CREATED)

        recipes = Recipe.objects.filter(user=self.user)
        self.assertEqual(recipes.count(),1)

        recipe = recipes[0]
        self.assertEqual(recipe.tags.count(),2)

        for tag in payload['tags']:
            exists = Tag.objects.filter(name=tag['name'],user=self.user)
            self.assertEqual(exists.count(),1)

    def test_create_recipe_with_existing_tags(self):
        """ create a new recipe with already existing tags """

        tag_indian = Tag.objects.create(user=self.user, name='Indian')

        payload= {
            'title':'Pongal',
            'time_minutes' : 20,
            'price' : Decimal('100'),
            'tags': [{'name':'Indian'}, {'name': 'Breakfast'}],
        }
        res = self.client.post(RECIPES_URL,payload,format='json')
        self.assertEqual(res.status_code,status.HTTP_201_CREATED)

        recipes = Recipe.objects.filter(user=self.user)
        self.assertEqual(recipes.count(),1)

        recipe = recipes[0]
        self.assertEqual(recipe.tags.count(),2)
        self.assertIn(tag_indian, recipe.tags.all())
        
    def test_update_tag_on_recipe(self):
        """ test update of tags on created recipe"""
        
        recipe = create_recipe(user=self.user)

        detail_url = create_detial_url(recipe.id)

        payload = {'tags':[{'name': 'Tag1'},{'name':'Tag2'}]}

        res = self.client.patch(detail_url,payload,format='json')
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        self.assertEqual(recipe.tags.count(),2)

        for tag in payload['tags']:
            exists = Tag.objects.filter(name=tag['name'],user=self.user)
            self.assertEqual(exists.count(),1)
    
    def test_update_existing_tag_on_recipe(self):
        """ Update the tags of a  recipe """

        tag_breakfast = Tag.objects.create(user=self.user,name='Breakfast')
        recipe = create_recipe(user=self.user)
        recipe.tags.add(tag_breakfast)

        tag_lunch = Tag.objects.create(user=self.user,name='Lunch')

        detail_url = create_detial_url(recipe.id)
        payload = {'tags':[{'name': 'Lunch'}]}
        res = self.client.patch(detail_url,payload,format='json')

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn(tag_lunch, recipe.tags.all())
        self.assertNotIn(tag_breakfast, recipe.tags.all())

    def test_clear_recipe_tags(self):
        """ Delete all tags of recipe """

        tag_breakfast = Tag.objects.create(user=self.user,name='Breakfast')
        recipe = create_recipe(user=self.user)
        recipe.tags.add(tag_breakfast)

        detail_url = create_detial_url(recipe.id)
        payload = {'tags':[]}
        res = self.client.patch(detail_url,payload,format='json')

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertNotIn(tag_breakfast, recipe.tags.all())
