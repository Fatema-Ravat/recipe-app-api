""" Views for User APIs """

from rest_framework import generics
from user.serializers import UserSerializer

class UserCreateAPIView(generics.CreateAPIView):
    """ View class for user create API """
    serializer_class = UserSerializer

