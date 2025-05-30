""" URLS mappings for recipe APIs """

from django.urls import path, include

from rest_framework.routers import DefaultRouter

from recipe import views


router = DefaultRouter()
router.register('recipes',views.RecipeAPIViewSet)
router.register('tags',views.TagAPIViewSet)
router.register('ingredients',views.IngredientAPIViewSet)

app_name ='recipe'

urlpatterns =[
    path('', include(router.urls)),
]