from rest_framework import serializers


class PreferencesSerializer(serializers.Serializer):
    desired_industries = serializers.ListField(child=serializers.CharField(), required=False)
    desired_size = serializers.ListField(child=serializers.CharField(), required=False)
    min_revenue = serializers.IntegerField(required=False)
    location = serializers.CharField(required=False)
    keywords = serializers.ListField(child=serializers.CharField(), required=False)
    min_growth = serializers.FloatField(required=False)
    weights = serializers.DictField(child=serializers.FloatField(), required=False)
from rest_framework import serializers
from .models import CorporateDisclosure

class CorporateDisclosureSerializer(serializers.ModelSerializer):
    class Meta:
        model = CorporateDisclosure
        fields = ['corp_name', 'disclosure_date', 'title', 'url']
