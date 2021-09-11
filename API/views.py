from django.db.models import F
from rest_framework.response import Response
from rest_framework import viewsets
from rest_framework import status

from .serializers import LinkSerializer
from ShortenerIndex.models import Link, Client
from ShortenerIndex.utils.utils import random_sequence, get_client_ip


class LinkViewSet(viewsets.ViewSet):
    """
    API view listing all users links
    """
    def retrieve(self, request, pk):
        url_output = pk  # Use more descriptive variable for url in our case
        user_ip = get_client_ip(request)
        try:
            queryset = Link.objects.filter(client__client_address=user_ip).get(url_output=url_output)
        except Link.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        serializer = LinkSerializer(queryset)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def list(self, request):
        user_ip = get_client_ip(request)
        queryset = Link.objects.filter(client__client_address=user_ip)
        serializer = LinkSerializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def create(self, request):
        user_ip = get_client_ip(request)

        # create user if he doesnt exist
        try:
            client = Client.objects.get(client_address=user_ip)
        except Client.DoesNotExist:
            selected_client = Client(client_address=user_ip)
            selected_client.save()
            client = Client.objects.get(client_address=user_ip)

        # If user has 5 or more links, deny request, send link limit reached message if possible
        if client.urls_count >= 5:
            return Response({"Fail": "5 link limit reached."}, status=status.HTTP_403_FORBIDDEN)

        # manually add server-generated fields
        request_data_added_client = request.data
        request_data_added_client['client'] = client
        request_data_added_client['url_output'] = random_sequence(10)

        serializer = LinkSerializer(data=request_data_added_client)
        if serializer.is_valid():
            Client.objects.filter(client_address=user_ip).update(urls_count=F('urls_count') + 1)
            serializer.save(client=client)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, pk):
        url_output = pk
        user_ip = get_client_ip(request)
        try:
            queryset = Link.objects.filter(client__client_address=user_ip).get(url_output=url_output)
        except Link.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        serializer = LinkSerializer(queryset)
        if not queryset:
            return Response(status=status.HTTP_404_NOT_FOUND)

        queryset.delete()
        Client.objects.filter(client_address=user_ip).update(urls_count=F('urls_count') - 1)
        return Response(serializer.data, status=status.HTTP_204_NO_CONTENT)
