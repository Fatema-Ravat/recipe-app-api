""" Serializer for User API view """

from django.contrib.auth import get_user_model, authenticate
from rest_framework import serializers

from django.utils.translation import gettext as _

class UserSerializer(serializers.ModelSerializer):
    """ Serializer for User model """

    class Meta:
        model = get_user_model()
        fields = ['email','password','username']
        extra_kwargs = {'password':{'write_only':True, 'min_length': 5}}

        def create(self,validated_data):
            """ Create a new user """

            print(validated_data)
            return get_user_model().objects.create_user(**validated_data)

        def update(self,instance,validated_data):
            """Retrieve update user """
            password = validated_data.pop('password',None)
            #usin pop() instead of get() removes password from validated_data
            user = super().update(instance,validated_data)

            if password:
                user.set_password(password)
                user.save()

            return user

class TokenSerializer(serializers.Serializer):
    """Serializer for the user auth token."""
    email = serializers.EmailField()
    password = serializers.CharField(
        style={'input_type': 'password'},
        trim_whitespace=False,
    )

    def validate(self, attrs):
        """Validate and authenticate the user."""
        email = attrs.get('email')
        password = attrs.get('password')

        user = authenticate(
            request=self.context.get('request'),
            username=email,
            password=password,
        )
        if not user:
            msg = _('Unable to authenticate with provided credentials.')
            raise serializers.ValidationError(msg, code='authorization')

        attrs['user'] = user
        return attrs

    