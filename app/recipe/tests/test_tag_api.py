""" Test for Tags API """

from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Tag
from recipe.serializers import TagSerializer

TAGS_URL = reverse('recipe:tag-list')

def get_detail_url(tag_id):
    """ create Tag detail url """
    return reverse('recipe:tag-detail', args=[tag_id])

def create_user(email='test@abc.com', password='testpass123'):
    """ create user function """
    return get_user_model().objects.create_user(email=email,password=password)

class PublicTagsAPITest(TestCase):
    """ Test for unauthenticated Tags API request"""

    def setUp(self):
        self.client = APIClient()
    
    def test_auth_required(self):
        """ Test that unauthorized user cannot list tags """
        res = self.client.get(TAGS_URL)
        
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

class PrivateTagsAPITest(TestCase):
    """ Tests for authenticated Tags API request """

    def setUp(self):
        self.client = APIClient()
        self.user = create_user()

        self.client.force_authenticate(self.user)

    def test_tag_list_api(self):
        """ test for list of Tags api  """
        Tag.objects.create(user=self.user, name='Tag1')
        Tag.objects.create(user=self.user, name='Tag2')
        
        res = self.client.get(TAGS_URL)

        self.assertEqual(res.status_code,status.HTTP_200_OK)

        tags = Tag.objects.all().order_by('-name')
        serializer = TagSerializer(tags, many=True)

        self.assertEqual(res.data,serializer.data)

    def test_tag_list_for_authorized_user_only(self):
        """ test to list tags of authenticated user only """

        new_user= create_user(email='new_user@abc.com')
        Tag.objects.create(user=new_user, name='Tag1')
        t1 = Tag.objects.create(user=self.user, name='Tag2')

        res = self.client.get(TAGS_URL)
        self.assertEqual(res.status_code,status.HTTP_200_OK)

        self.assertEqual(len(res.data),1)
        self.assertEqual(res.data[0]['name'],t1.name)
        self.assertEqual(res.data[0]['id'],t1.id)

    def test_update_tag(self):
        """ test for update the Tag api"""
        tag = Tag.objects.create(user=self.user,name='After Dinner')

        payload={'name':'Dessert'}

        url = get_detail_url(tag.id)
        res = self.client.patch(url, payload)
        self.assertEqual(res.status_code,status.HTTP_200_OK)

        tag.refresh_from_db()
        self.assertEqual(tag.name, payload['name'])


    def test_delete_tag(self):
        """ test to delete Tag api """
        tag = Tag.objects.create(user=self.user,name='To be Deleted')
        url = get_detail_url(tag.id)
        res = self.client.delete(url)

        self.assertEqual(res.status_code,status.HTTP_204_NO_CONTENT)

        self.assertFalse(Tag.objects.filter(id=tag.id).exists())




    

