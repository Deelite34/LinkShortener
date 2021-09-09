from django.conf import settings
from django.test import TestCase, Client
from django.urls import reverse

from ..models import Link
from ..models import Client as model_client
from .test_models import LinkTest, ClientTest

DOMAIN = settings.DEFAULT_DOMAIN[:-1]


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
        Tests if correct entry is created in database, as well as related user
        and redirection from shortened link to corresponding website
        """
        url_to_input = 'www.onet.pl'
        c = Client()

        c.post(reverse('index'), data={'url_input': url_to_input})
        created_link = Link.objects.get(url_input=url_to_input)
        created_user = Link.objects.get(url_input=url_to_input).client
        response = self.client.get(f"{DOMAIN}/l/{created_link.url_output}")

        self.assertEqual(created_link.url_input, url_to_input)
        self.assertEqual(response.status_code, 301)
        self.assertIsNotNone(created_user)

    def test_user_banned_link_creation(self):
        """
        Shorten a link and set its owner to banned.
        then try post again, assert that no new information was added to db
        """
        url_to_input = 'www.google.com'
        url_to_input_2 = 'www.google.pl'
        c = Client()

        c.post(reverse('index'), data={'url_input': url_to_input})
        user_object = model_client.objects.get(link__url_input=url_to_input)
        user_object.is_banned = True
        user_object.save()
        response = c.post(reverse('index'), data={'url_input': url_to_input_2})
        banned_user_new_link_exists = Link.objects.filter(url_input=url_to_input_2).exists()

        self.assertEqual(response.status_code, 403)
        self.assertTrue(user_object.is_banned)
        self.assertFalse(banned_user_new_link_exists)

    def test_link_limit(self):
        """
        Create 5 links, and test if no more can be created
        """
        url_to_input = 'www.google.com'
        c = Client()

        for i in range(6):
            c.post(reverse('index'), data={'url_input': url_to_input})
        response = c.post(reverse('index'), data={'url_input': url_to_input})
        all_posts = Link.objects.all().count()

        self.assertEqual(response.status_code, 403)
        self.assertEqual(all_posts, 5)


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

    def test_link_deletion_on_post(self):
        """
        Test deleting users own links with post request to redirect view
        """
        c = Client()
        url_to_input = "www.wp.pl"

        c.post(reverse('index'), data={'url_input': url_to_input})
        user_object = model_client.objects.get(link__url_input=url_to_input)
        found_url_output = Link.objects.get(url_input=url_to_input)
        c.post(reverse('redirect', kwargs={'url_output': found_url_output.url_output}))
        result = Link.objects.filter(url_input=url_to_input).exists()

        self.assertEqual(user_object.urls_count, 1)
        self.assertFalse(result)

    def test_delete_other_users_link(self):
        """
        Try to delete other users post, and test the response
        """
        c_1 = Client()
        c_2 = Client()
        url_to_input = "www.wp.pl"
        url_to_input_2 = "www.google.pl"

        # create users by posting links, so we get their IP addressess
        c_1.post(reverse('index'), data={'url_input': url_to_input})
        c_2.post(reverse('index'), data={'url_input': url_to_input_2})
        # edit c_2 ip address from the local ip to custom one to simulate different user
        user_object = model_client.objects.get(link__url_input=url_to_input_2)
        user_object.client_address = '12.23.34.45'
        user_object.save()
        found_url_output = Link.objects.get(url_input=url_to_input)
        response = c_2.post(reverse('redirect', kwargs={'url_output': found_url_output.url_output}))
        post_exists = Link.objects.get(url_input=url_to_input)

        self.assertEqual(response.status_code, 403)
        self.assertTrue(post_exists)