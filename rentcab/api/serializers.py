from django.contrib.auth import get_user_model
from rest_framework import serializers


# Serializers define the API representation.
class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = get_user_model()
        fields = ["url", "username", "email", "is_staff"]
