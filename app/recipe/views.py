""" Views for recipe apis  """

from rest_framework import viewsets
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from recipe import serializers
from core.models import Recipe

class RecipeAPIViewSet(viewsets.ModelViewSet):
    """ View to manage Recipe APIs """

    serializer_class = serializers.RecipeDetailSerializer
    queryset = Recipe.objects.all()
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Retrieve recipes for authenticated user."""
        return super().get_queryset().filter(user=self.request.user).order_by('-id')

    def get_serializer_class(self):
        """ method that returns which serializer class is used """
        if self.action == 'list':
            return serializers.RecipeSerializer
        
        return super().get_serializer_class()

    def perform_create(self, serializer):
        """ Create new recipe """
        serializer.save(user=self.request.user)

    
