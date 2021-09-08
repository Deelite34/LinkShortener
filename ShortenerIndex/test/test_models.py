from django.test import TestCase

from ..models import Link
from ..models import Client as model_client


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
