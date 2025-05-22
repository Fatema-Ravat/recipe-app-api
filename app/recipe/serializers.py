""" Serializers for recipe apis """

from rest_framework import serializers

from core.models import Recipe

class RecipeSerializer(serializers.ModelSerializer):
    """ serializer for listing recipe model """

    class Meta:
        model = Recipe
        fields = ['id','title','time_minutes','price','link']
        read_only_fields = ['id']

# inorder to avoid duplicating the above code for this serializer we just extend from it.
class RecipeDetailSerializer(RecipeSerializer):
    """ serializer for detail view recipe model """
    class Meta(RecipeSerializer.Meta):
        fields = RecipeSerializer.Meta.fields + ['description']
