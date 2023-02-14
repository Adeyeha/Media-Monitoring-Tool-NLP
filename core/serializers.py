from rest_framework import serializers
from .models import news
class newsserializer(serializers.ModelSerializer):
    class Meta:
        model = news
        fields = ['search_subject','timestamp']