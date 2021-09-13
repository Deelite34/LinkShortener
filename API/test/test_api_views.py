from django.urls import reverse
from rest_framework.test import APITestCase

from ShortenerIndex.models import Link, Client
from ShortenerIndex.utils.utils import random_sequence
from rest_framework import status


class TestAPIViewSet(APITestCase):
    """
    Tests the API module.
    Uses AAA (Arrange Act Assert) pattern for organising parts of code for each test
    """
    def setUp(self):
        """
        Arrange step used by most of API tests. Some tests need additional arrange steps and will have
        their own extension of arrange step, for other tests setUp will do everything needed for initial
        arrangements.
        Prepares Link and Client entities, creates variables used in other tests.
        """
        # Arrange
        self.default_url_input = 'www.wp.pl'
        self.alternative_url_input = 'www.google.com'
        self.default_client_address = '127.0.0.1'  # Local ip address,be careful for possibilities of it being different

        self.default_test_link_url_output = random_sequence(10)
        self.alternative_test_link_url_output = random_sequence(10)

        kwargs = {
            'pk': self.default_test_link_url_output
        }

        self.test_client = Client(client_address=self.default_client_address, urls_count=2)
        self.test_client.save()

        link_1 = Link(url_input=self.default_url_input,
                      url_output=self.default_test_link_url_output,
                      client=self.test_client)
        link_2 = Link(url_input=self.alternative_url_input,
                      url_output=self.alternative_test_link_url_output,
                      client=self.test_client)
        link_1.save()
        link_2.save()

        self.list_url = reverse('links-list')
        self.test_link_detail_url = reverse('links-detail', kwargs=kwargs)

    def test_list_view(self):
        """
        Tests correct status code, and presence of 2 items in listed items
        """
        # Act
        response = self.client.get(self.list_url, format='json')

        # Assert
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_retrieve_view(self):
        """
        Tests status codes, retrieved item containing correct amount of correct data
        """
        # Act
        get_note = self.client.get(self.test_link_detail_url)
        get_nonexistant_note = self.client.get('asdfASDFas')

        # Assert
        self.assertEqual(get_note.status_code, status.HTTP_200_OK)
        self.assertEqual(len(get_note.data), 3)  # 3 displayed fields of created item
        self.assertEqual(get_note.data['url_output'], self.default_test_link_url_output)
        self.assertEqual(get_note.data['url_input'], self.default_url_input)
        self.assertEqual(get_nonexistant_note.status_code, status.HTTP_404_NOT_FOUND)

    def test_create_view(self):
        """
        Tests status codes, length of data returned after creation of Link,
        Custom 403 code error message, and correct count of Links linked to Client.
        """
        # Arrange
        correct_data = {'url_input': 'www.youtube.com'}
        incorrect_data = {'this_field_doesnt_exist': 'asdf'}
        incorrect_data_2 = {'url_input': 'ąęąś'}

        # Act
        response_correct_data = self.client.post(self.list_url, data=correct_data, format='json')
        response_incorrect_data = self.client.post(self.list_url, data=incorrect_data, format='json')
        response_incorrect_data_2 = self.client.post(self.list_url, data=incorrect_data_2, format='json')
        response_excess_data_test_fourth_item = self.client.post(self.list_url, data=correct_data, format='json')
        response_excess_data_test_fifth_item = self.client.post(self.list_url, data=correct_data, format='json')
        response_excess_data_test_sixth_item = self.client.post(self.list_url, data=correct_data, format='json')
        test_client_data = Client.objects.get(client_address=self.default_client_address)

        # Assert
        self.assertEqual(response_correct_data.status_code, status.HTTP_201_CREATED)
        self.assertEqual(len(response_correct_data.data), 3)  # 3 columns from single Link model row in db
        self.assertEqual(response_incorrect_data.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response_incorrect_data_2.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response_excess_data_test_fourth_item.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response_excess_data_test_fifth_item.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response_excess_data_test_sixth_item.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response_excess_data_test_sixth_item.data['Fail'], '5 link limit reached.')
        self.assertEqual(test_client_data.urls_count, 5)

    def test_destroy_view(self):
        """
        Tests status codes, correct urls_count field value for main user, and alternative user
        """
        # Arrange
        alternative_client_address = '1.2.3.4'
        alternative_test_client = Client(client_address=alternative_client_address, urls_count=1)
        alternative_test_client.save()
        alternative_link_output_url_sequence = random_sequence(10)
        alternative_link = Link(url_input=self.default_url_input,
                                url_output=alternative_link_output_url_sequence,
                                client=alternative_test_client)
        alternative_link.save()
        alternative_link_url = reverse('links-detail', kwargs={'pk': alternative_link_output_url_sequence})
        nonexistant_link_url = reverse('links-detail', kwargs={'pk': random_sequence(10)})

        # Act
        response_delete_own_link = self.client.delete(self.test_link_detail_url, format='json')
        response_delete_not_own_link = self.client.delete(alternative_link_url, format='json')
        response_delete_nonexistant_link = self.client.delete(nonexistant_link_url, format='json')
        test_client_data = Client.objects.get(client_address=self.default_client_address)

        # Assert
        self.assertEqual(response_delete_own_link.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(response_delete_not_own_link.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response_delete_nonexistant_link.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(test_client_data.urls_count, 1)
        self.assertEqual(alternative_test_client.urls_count, 1)
