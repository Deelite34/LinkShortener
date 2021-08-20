from django.test import TestCase
from django.test import Client
from django.urls import reverse
from django.conf import settings

from .models import Link
from .models import Client as model_client

from .forms import ShortenLinkForm


DOMAIN = settings.DEFAULT_DOMAIN[:-1]

"""
Model tests
"""


class LinkTest(TestCase):

    @staticmethod
    def create_link(url_input="www.wp.pl", url_output="abcdeFGHIJ"):
        return Link.objects.create(url_input=url_input, url_output=url_output)

    def test_link_creation(self):
        test_link = LinkTest.create_link()
        link_model_str_func_result = test_link.__str__()
        link_model_expected_str_result = f"{test_link.url_input} ({test_link.operation})"

        checked_link_instance = isinstance(test_link, Link)

        self.assertTrue(checked_link_instance)
        self.assertEqual(link_model_str_func_result, link_model_expected_str_result)


class ClientTest(TestCase):

    def create_client(self):
        return model_client.objects.create()

    def test_client_creation(self):
        test_client = self.create_client()
        client_model_str_func_result = test_client.__str__()
        client_model_expected_str_result = f"user {test_client.client}"

        check_client_instance = isinstance(test_client, model_client)

        self.assertTrue(check_client_instance)
        self.assertEqual(client_model_str_func_result, client_model_expected_str_result)


"""
View tests
"""


class TestIndexView(TestCase):
    def test_index_page_get(self):
        base_url = DOMAIN

        response = self.client.get(base_url)

        self.assertEqual(response.status_code, 200)

    def test_index_page_post(self):
        # Post correct data, that should result in creation of entry in database
        # Tests if correct entry is created in database, and redirection to that website
        url_to_input = 'www.onet.pl'
        c = Client()

        c.post(reverse('index'), data={'url_input': url_to_input})
        created_link = Link.objects.get(url_input=url_to_input)
        response = self.client.get(f"{DOMAIN}/l/{created_link.url_output}")

        self.assertEqual(created_link.url_input, url_to_input)
        self.assertEqual(response.status_code, 301)


class TestRedirectView(TestCase):

    def test_link_redirection_without_http_prefix(self):
        url_to_input = "www.youtube.com"
        url_to_output = "QWEQWEqweq"
        LinkTest.create_link(url_input=url_to_input, url_output=url_to_output)
        created_link = Link.objects.get(url_input=url_to_input)
        subpage = reverse('redirect', args=[created_link.url_output])
        full_url = DOMAIN + subpage
        expected_url = f"{DOMAIN}/l/{url_to_output}/"

        response = self.client.get(full_url)
        end_response = self.client.get(full_url, follow=True)

        self.assertEqual(full_url, expected_url)
        self.assertEqual(response.status_code, 302)
        self.assertNotEqual(end_response, 404)

    def test_link_redirection_with_http_prefix(self):
        url_to_input = 'http://reddit.com'
        url_to_output = 'asdfASDFas'
        LinkTest.create_link(url_input=url_to_input, url_output=url_to_output)
        created_link_secondary = Link.objects.get(url_input=url_to_input)
        subpage = reverse('redirect', args=[created_link_secondary.url_output])
        full_url = DOMAIN + subpage
        expected_url = f"{DOMAIN}/l/{url_to_output}/"

        response_secondary = self.client.get(full_url)
        end_response_secondary = self.client.get(full_url, follow=True)

        self.assertEqual(full_url, expected_url)
        self.assertEqual(response_secondary.status_code, 302)
        self.assertNotEqual(end_response_secondary, 404)


"""
form tests
"""


class TestShortenLinkForm(TestCase):

    def test_form_is_valid(self):
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
        data_invalid_1 = {'url_input': 'https://www.123213.com/'}
        data_invalid_2 = {'url_input': 'https://www.!@#$!@%@&*.com/'}
        data_invalid_3 = {'url_input': 'https://www.ąęółźżć.com/'}

        form_invalid_1 = ShortenLinkForm(data=data_invalid_1)
        form_invalid_2 = ShortenLinkForm(data=data_invalid_2)
        form_invalid_3 = ShortenLinkForm(data=data_invalid_3)

        self.assertFalse(form_invalid_1.is_valid())
        self.assertFalse(form_invalid_2.is_valid())
        self.assertFalse(form_invalid_3.is_valid())
