from rest_framework import serializers
from user.serializers import UserSerializer
from .models import Test


class TestSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = Test
        fields = "__all__"

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        ret.pop("user", None)
        return ret