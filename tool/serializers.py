from rest_framework import serializers
from user.serializers import UserSerializer
from .models import Test


class TestSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    revenue_impact = serializers.SerializerMethodField()

    def get_revenue_impact(self, obj):
        if obj.control_revenue and obj.control_revenue > 0:
            return ((obj.test_revenue - obj.control_revenue) / obj.control_revenue) * 100
        return None

    class Meta:
        model = Test
        fields = "__all__"

    def to_representation(self, instance):
        ret = super().to_representation(instance)

        ret.pop("user", None)

        revenue_impact = self.get_revenue_impact(instance)
        if revenue_impact is not None:
            ret['revenue_impact'] = revenue_impact
            
        return ret