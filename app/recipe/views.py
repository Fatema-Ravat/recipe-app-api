""" Views for recipe apis  """

from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import viewsets, mixins, status
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from recipe import serializers
from core.models import Recipe, Tag, Ingredient


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
        elif self.action == 'upload_image':
            return serializers.RecipeImageSerializer
        
        return super().get_serializer_class()

    def perform_create(self, serializer):
        """ Create new recipe """
        serializer.save(user=self.request.user)

    @action(methods=['POST'],detail=True,url_path='upload-image')
    def upload_image(self,request,pk=None):
        """ Uplaod image to recipe """
        recipe = self.get_object()
        serializer = self.get_serializer(recipe,data=request.data)

        
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status = status.HTTP_200_OK)
        
        return Response(serializer.errors,status= status.HTTP_400_BAD_REQUEST)


class BaseRecipeAttrViewSet(mixins.UpdateModelMixin,
                            mixins.DestroyModelMixin,
                            mixins.ListModelMixin,
                            viewsets.GenericViewSet):
    """ Base class for Recipe Attributes """

    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Retrieve Tags for authenticated user."""
        return super().get_queryset().filter(user=self.request.user).order_by('-name')

class TagAPIViewSet(BaseRecipeAttrViewSet):
    """ View to manage Tag model APIs """

    queryset = Tag.objects.all()
    serializer_class = serializers.TagSerializer
    
    
class IngredientAPIViewSet(BaseRecipeAttrViewSet):
    """ View to manage Ingredient model APIs """

    queryset = Ingredient.objects.all()
    serializer_class = serializers.IngredientSerializer
    