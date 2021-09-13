from rest_framework import serializers
from ShortenerIndex.models import Link


class LinkSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Link
        fields = ('url_input', 'url_output', 'creation_date')

