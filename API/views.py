from django.db.models import F
from rest_framework.decorators import action
from rest_framework.parsers import MultiPartParser
from rest_framework.response import Response
from rest_framework import viewsets
from rest_framework import status

from .serializers import LinkSerializer
from ShortenerIndex.models import Link, Client
from ShortenerIndex.utils.utils import random_sequence, get_client_ip
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema


url_input = openapi.Parameter('url_input', in_=openapi.IN_BODY, type=openapi.TYPE_STRING)

category_response = openapi.Response('Data of the specific retrieved Link', LinkSerializer)


class LinkViewSet(viewsets.ViewSet):
    """
    Viewset for the application API
    """
    @swagger_auto_schema(
        type=openapi.TYPE_STRING,
        parameters=['url_input'],
        name='url_input',
        operation_description='Returns details of single Link of the user making the request. ' +
                              'In the field "ID" input the "url_output" value of the specific shortened link.',
        responses={
            200: LinkSerializer(many=True),
            404: "Link not found"
        },
        tags=['Links'],
    )
    def retrieve(self, request, pk):
        """
        Returns details of single Link of the user making the request.
        """
        url_output = pk  # Use more descriptive variable for url in our case
        user_ip = get_client_ip(request)
        try:
            queryset = Link.objects.filter(client__client_address=user_ip).get(url_output=url_output)
        except Link.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        serializer = LinkSerializer(queryset)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        type=openapi.TYPE_STRING,
        responses={200: LinkSerializer(many=True)},
        tags=['Links'],
    )
    def list(self, request):
        """
        Returns all links of the user making the request.
        """
        user_ip = get_client_ip(request)
        queryset = Link.objects.filter(client__client_address=user_ip)
        serializer = LinkSerializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['url_input'],
            properties={
                'url_input': openapi.Schema(type=openapi.TYPE_STRING)
            }),
        responses={
            201: LinkSerializer(many=True),
            400: 'Bad request',
            403: 'Forbidden'
        },
        tags=['Links'],
    )
    def create(self, request):
        """
        Creates a link of the user making the request and updates users url_count value.
        Requires request to cointain 'url_input': 'value' field,
        where value is the URL to be shortened.
        """
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

    @swagger_auto_schema(
        operation_description='Deletes a link of the user making the request and updates users url_count value. ' +
                              'In the field ID input the url_output of the specific shortened link.',
        responses={
            204: "No content",
            404: "Not found"
        },
        tags=['Links'],
    )
    def destroy(self, request, pk):
        """
        Deletes a link of the user making the request and updates users url_count value.
        """
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
