""" Views for User APIs """

from rest_framework import generics, permissions, authentication
from rest_framework.settings import api_settings

from rest_framework.authtoken.views import ObtainAuthToken

from user.serializers import UserSerializer,TokenSerializer

class UserCreateAPIView(generics.CreateAPIView):
    """ View class for user create API """
    serializer_class = UserSerializer

class UserCreateTokenView(ObtainAuthToken):
    """ View to generate user token """
    serializer_class = TokenSerializer
    renderer_classes = api_settings.DEFAULT_RENDERER_CLASSES

class UserManageAPIView(generics.RetrieveUpdateAPIView):
    """ View to retrieve and update an user """

    serializer_class = UserSerializer
    authentication_classes =[authentication.TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        """ Retrieve and return authenticated user """
        return self.request.user