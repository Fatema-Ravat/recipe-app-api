""" Serializers for recipe apis """

from rest_framework import serializers

from core.models import Recipe,Tag, Ingredient

class TagSerializer(serializers.ModelSerializer):
    """ Serializer for listing Tag model """

    class Meta:
        model = Tag
        fields = ['id','name']
        read_only_fields = ['id']

class IngredientSerializer(serializers.ModelSerializer):
    """ Serializer for listing Ingredient model """

    class Meta:
        model = Ingredient
        fields = ['id','name']
        read_only_fields = ['id']

class RecipeSerializer(serializers.ModelSerializer):
    """ serializer for listing recipe model """
    tags = TagSerializer(many=True, required=False)
    ingredients = IngredientSerializer(many=True, required= False)

    class Meta:
        model = Recipe
        fields = ['id','title','time_minutes','price',
                  'calories_per_serving','link','tags','ingredients','image']
        read_only_fields = ['id']

    def _get_or_create_tags(self, tags, recipe):
        """ Method to get or create tags for a recipe """

        auth_user = self.context['request'].user

        for tag in tags:
            tag_obj, created = Tag.objects.get_or_create(user=auth_user, **tag)
            recipe.tags.add(tag_obj)

    def _get_or_create_ingredients(self,ingredients,recipe):
        """ Internal method to get/create ingredient for  a recipe """
        
        auth_user = self.context['request'].user
        for ing in ingredients:
            ing_obj,created = Ingredient.objects.get_or_create(user=auth_user,**ing)
            recipe.ingredients.add(ing_obj)

    def create(self,validated_data):
        """ create a recipe """
        tags = validated_data.pop('tags',[])
        ingredients = validated_data.pop('ingredients',[])
        recipe = Recipe.objects.create(**validated_data)
        self._get_or_create_tags(tags,recipe)
        self._get_or_create_ingredients(ingredients,recipe)

        return recipe

    def update(self,instance,validated_data):
        """ Update recipe"""

        tags = validated_data.pop('tags',None)
        ingredients = validated_data.pop('ingredients',None)
        if tags is not None:
            instance.tags.clear()
            self._get_or_create_tags(tags,instance)

        if ingredients is not None:
            instance.ingredients.clear()
            self._get_or_create_ingredients(ingredients,instance)

        
        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()
        return instance


# inorder to avoid duplicating the above code for this serializer we just extend from it.
class RecipeDetailSerializer(RecipeSerializer):
    """ serializer for detail view recipe model """
    class Meta(RecipeSerializer.Meta):
        fields = RecipeSerializer.Meta.fields + ['description']

class RecipeImageSerializer(serializers.ModelSerializer):
    """ serializer for image field of Recipe model """

    class Meta:
        model = Recipe
        fields =['id','image']
        read_only_fields = ['id']
        extra_kwargs = {'image':{'required':True}}


