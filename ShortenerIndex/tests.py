import string

from django.test import TestCase
from django.test import Client
from django.urls import reverse
from django.conf import settings

from .models import Link
from .models import Client as model_client
from .forms import ShortenLinkForm
from .utils.utils import random_sequence

DOMAIN = settings.DEFAULT_DOMAIN[:-1]


"""
Model tests
"""


def create_default_user_link_pair():
    """
    Helper function that creates related pair of client and link models.
    Returns tuple consisting of client as first element, and link as second one
    """
    test_client = ClientTest.create_client()
    test_link = LinkTest.create_link(client_instance=test_client)
    return test_client, test_link


class LinkTest(TestCase):

    @staticmethod
    def create_link(url_input="www.wp.pl", url_output="abcdeFGHIJ", client_instance=None):
        """
        Static method that creates Link model object using parameters and returns reference to that object
        """
        return Link.objects.create(url_input=url_input, url_output=url_output, client=client_instance)

    def test_link_creation(self):
        """
        Tests creating Link model, and __str__ function of that model.
        """
        client_link_pair = create_default_user_link_pair()
        link_model_str_func_result = client_link_pair[1].__str__()
        link_model_expected_str_result = f"{client_link_pair[1].url_input} (1)"

        is_link_instance = isinstance(client_link_pair[1], Link)

        self.assertTrue(is_link_instance)
        self.assertEqual(link_model_str_func_result, link_model_expected_str_result)


class ClientTest(TestCase):
    @staticmethod
    def create_client(test_ip='123.456.789'):
        """
        Static method that creates Client model object using parameters, and returns reference to that object
        """
        return model_client.objects.create(client_address=test_ip)

    def test_client_creation(self):
        """
        Tests creating Client model, and __str__ function of that model.
        """
        test_client = self.create_client()
        client_model_str_func_result = test_client.__str__()
        client_model_expected_str_result = f"user-1"

        is_client_instance = isinstance(test_client, model_client)

        self.assertTrue(is_client_instance)
        self.assertEqual(client_model_str_func_result, client_model_expected_str_result)


"""
View tests
"""


class TestIndexView(TestCase):
    def test_index_page_get(self):
        """
        If index page is accessible, it should return 200 status
        """
        base_url = DOMAIN

        response = self.client.get(base_url)

        self.assertEqual(response.status_code, 200)

    def test_index_page_post(self):
        """
        Posts correct data, that should result in creation of entry in database
        Tests if correct entry is created in database,
        and redirection from shortened link to corresponding website
        """
        url_to_input = 'www.onet.pl'
        c = Client()

        c.post(reverse('index'), data={'url_input': url_to_input})
        created_link = Link.objects.get(url_input=url_to_input)
        response = self.client.get(f"{DOMAIN}/l/{created_link.url_output}")

        self.assertEqual(created_link.url_input, url_to_input)
        self.assertEqual(response.status_code, 301)


class TestRedirectView(TestCase):

    def test_link_redirection_without_http_prefix(self):
        """
        Tests redirection from our website subpage, to intended URL (without http prefix).
        """
        url_to_input = "www.youtube.com"
        url_to_output = "QWEQWEqweq"
        test_user = ClientTest.create_client()
        test_link = LinkTest.create_link(url_input=url_to_input, url_output=url_to_output, client_instance=test_user)
        subpage = reverse('redirect', args=[test_link.url_output])
        full_url = DOMAIN + subpage
        expected_url = f"{DOMAIN}/l/{url_to_output}/"

        response = self.client.get(full_url)

        self.assertEqual(full_url, expected_url)
        self.assertEqual(response.status_code, 302)

    def test_link_redirection_with_http_prefix(self):
        """
        Tests redirection from our website subpage, to intended URL (with http prefix).
        """
        url_to_input = 'http://reddit.com'
        url_to_output = 'asdfASDFas'
        test_client = ClientTest.create_client()
        LinkTest.create_link(url_input=url_to_input, url_output=url_to_output, client_instance=test_client)
        created_link = Link.objects.get(url_input=url_to_input)
        subpage = reverse('redirect', args=[created_link.url_output])
        full_url = DOMAIN + subpage
        expected_url = f"{DOMAIN}/l/{url_to_output}/"

        response = self.client.get(full_url)

        self.assertEqual(full_url, expected_url)
        self.assertEqual(response.status_code, 302)


# form tests

class TestShortenLinkForm(TestCase):

    def test_form_is_valid(self):
        """
        Test correct cases if inputed URLs
        """
        data_valid_1 = {'url_input': 'https://www.yahoo.com/'}
        data_valid_2 = {'url_input': 'http://www.yahoo.com/'}
        data_valid_3 = {'url_input': 'yahoo.com'}

        form_valid_1 = ShortenLinkForm(data=data_valid_1)
        form_valid_2 = ShortenLinkForm(data=data_valid_2)
        form_valid_3 = ShortenLinkForm(data=data_valid_3)

        self.assertTrue(form_valid_1.is_valid())
        self.assertTrue(form_valid_2.is_valid())
        self.assertTrue(form_valid_3.is_valid())

    def test_form_is_not_valid(self):
        """
        Test incorrect cases if inputed URLs
        """
        data_invalid_1 = {'url_input': 'https://www.123213.com/'}
        data_invalid_2 = {'url_input': 'https://www.!@#$!@%@&*.com/'}
        data_invalid_3 = {'url_input': 'https://www.ąęółźżć.com/'}

        form_invalid_1 = ShortenLinkForm(data=data_invalid_1)
        form_invalid_2 = ShortenLinkForm(data=data_invalid_2)
        form_invalid_3 = ShortenLinkForm(data=data_invalid_3)

        self.assertFalse(form_invalid_1.is_valid())
        self.assertFalse(form_invalid_2.is_valid())
        self.assertFalse(form_invalid_3.is_valid())


class TestUtils(TestCase):
    """
    Tests utility functions from utils.py file
    """
    def test_random_sequence(self):
        length = 10
        test_sequence = random_sequence(length)
        uses_correct_signs = True

        for letter in test_sequence:
            if letter not in string.ascii_letters:
                uses_correct_signs = False
                break
        has_correct_length = len(test_sequence) == length

        self.assertTrue(uses_correct_signs)
        self.assertTrue(has_correct_length)
