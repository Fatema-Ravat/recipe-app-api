""" Core models """

import os
import uuid
from django.conf import settings
from django.db import models
from django.contrib.auth.models import (AbstractBaseUser,
                                 PermissionsMixin,
                                 BaseUserManager, )

def recipe_image_file_path(instance, filename):
    """ Function to generate unique filename and filepath for image """
    extention = os.path.splitext(filename)[1]
    filename = f'{uuid.uuid4()}{extention}'

    return os.path.join('uploads','recipe',filename)


class UserManager(BaseUserManager):
    """ Manager for user object """

    def create_user(self, email, password = None, **extra_fields):
        """ Create save and return the user"""

        if not email:
            raise ValueError("User must have email address")
        user = self.model(email=self.normalize_email(email), **extra_fields)
        user.set_password(password)
        user.save(using=self._db)

        return user
    
    def create_superuser(self,email,password):
        """ Create and save super user """
        user = self.create_user(email=email,password=password)
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)

        return user



class User(AbstractBaseUser, PermissionsMixin):
    """ Custom user class """

    email = models.EmailField(max_length=255, unique=True)
    username = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = UserManager()
    USERNAME_FIELD = 'email'

class Recipe(models.Model):
    """ Model for Recipe """
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete = models.CASCADE,)
    title = models.CharField(max_length = 255)
    description = models.TextField(blank=True)
    time_minutes = models.IntegerField()
    price = models.DecimalField(max_digits=5,decimal_places=2)
    calories_per_serving = models.IntegerField(blank=True)
    link = models.CharField(max_length = 255, blank = True)
    tags = models.ManyToManyField('Tag')
    ingredients = models.ManyToManyField('Ingredient')
    image = models.ImageField(null = True, upload_to = recipe_image_file_path)

    def __str__(self):
        return self.title

class Tag(models.Model):
    """ Model for Tags for filtering recipes """
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete = models.CASCADE)
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name
    
class Ingredient(models.Model):
    """ Model for Ingredients for recipes """

    user= models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name