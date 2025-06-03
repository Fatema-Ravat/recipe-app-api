""" Views for recipe apis  """

from drf_spectacular.utils import (
    extend_schema_view,
    extend_schema,
    OpenApiParameter,
    OpenApiTypes,
)

from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import viewsets, mixins, status
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from recipe import serializers
from core.models import Recipe, Tag, Ingredient

@extend_schema_view(
    list=extend_schema(
        parameters=[
            OpenApiParameter(
                'tags',
                OpenApiTypes.STR,
                description='Comma separated list of tag IDs to filter',
            ),
            OpenApiParameter(
                'ingredients',
                OpenApiTypes.STR,
                description='Comma separated list of ingredient IDs to filter',
            ),
        ]
    )
)


class RecipeAPIViewSet(viewsets.ModelViewSet):
    """ View to manage Recipe APIs """

    serializer_class = serializers.RecipeDetailSerializer
    queryset = Recipe.objects.all()
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def _get_int_list_from_str(self,qs):
        """ Returns the int list of the , separated string values passed"""
        return [int(str_id) for str_id in qs.split(',')]

    def get_queryset(self):
        """Retrieve recipes for authenticated user."""
        # return super().get_queryset().filter(user=self.request.user).order_by('-id')
        queryset = super().get_queryset()
        tags = self.request.query_params.get('tags')
        ingredients = self.request.query_params.get('ingredients')

        if tags:
            tag_ids = self._get_int_list_from_str(tags)
            queryset = queryset.filter(tags__id__in = tag_ids)
        if ingredients:
            ingredient_ids = self._get_int_list_from_str(ingredients)
            queryset = queryset.filter(ingredients__id__in = ingredient_ids)
        
        return queryset.filter(user=self.request.user).order_by('-id').distinct()


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
    