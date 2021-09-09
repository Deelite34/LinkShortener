from django.test import TestCase

from ..forms import ShortenLinkForm


class TestShortenLinkForm(TestCase):

    def test_form_is_valid(self):
        """
        Test correct cases if inputed URLs
        """
        data_valid_1 = {'url_input': 'https://www.yahoo.com/'}
        data_valid_2 = {'url_input': 'http://www.yahoo.com/'}
        data_valid_3 = {'url_input': 'www.yahoo.com'}
        data_valid_4 = {'url_input': 'yahoo.com'}

        form_valid_1 = ShortenLinkForm(data=data_valid_1)
        form_valid_2 = ShortenLinkForm(data=data_valid_2)
        form_valid_3 = ShortenLinkForm(data=data_valid_3)
        form_valid_4 = ShortenLinkForm(data=data_valid_4)

        self.assertTrue(form_valid_1.is_valid())
        self.assertTrue(form_valid_2.is_valid())
        self.assertTrue(form_valid_3.is_valid())
        self.assertTrue(form_valid_4.is_valid())

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