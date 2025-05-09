""" Urls for user API """

from django.urls import path
from user import views

app_name = 'user'

urlpatterns = [
        path('create/',views.UserCreateAPIView.as_view(),name='create'),
        path('token/',views.UserCreateTokenView.as_view(),name='token'),
        path('me/',views.UserManageAPIView.as_view(),name='me'),
]

