from rest_framework import serializers
from .models import CorporateDisclosure

class CorporateDisclosureSerializer(serializers.ModelSerializer):
    class Meta:
        model = CorporateDisclosure
        fields = ['corp_name', 'disclosure_date', 'title', 'url']
