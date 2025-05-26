""" Views for recipe apis  """

from rest_framework import viewsets, mixins
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from recipe import serializers
from core.models import Recipe, Tag

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

class TagAPIViewSet(mixins.UpdateModelMixin,
                 mixins.DestroyModelMixin,
                 mixins.ListModelMixin,
                 viewsets.GenericViewSet):
    """ View to manage Tag model APIs """

    queryset = Tag.objects.all()
    serializer_class = serializers.TagSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Retrieve Tags for authenticated user."""
        return super().get_queryset().filter(user=self.request.user).order_by('-name')
    
    
