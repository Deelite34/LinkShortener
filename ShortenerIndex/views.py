from django.http import HttpResponse, HttpResponseRedirect, HttpResponseForbidden
from django.shortcuts import render
from django.urls import reverse
from django.views import View

from .forms import ShortenLinkForm
from .models import Link, Client

from .utils.utils import random_sequence, get_client_ip


class IndexView(View):

    def get(self, request):
        """
        Main webpage view accessed with GET request.
        Displays empty form, attempts to display user links
        """
        form = ShortenLinkForm()
        client_ip = get_client_ip(request)
        current_user_data = Link.objects.filter(client__client_address=client_ip).select_related('client')
        base_url = request.build_absolute_uri('/l/')
        context = {
            'form': form,
            'current_user_data': current_user_data,
            'base_url': base_url,
        }

        return render(request, 'ShortenerIndex/index.html', context=context)

    def post(self, request):
        """
        View for POST request with link shortening form on main webpage.
        Checks if user is permited to generate links,
        generates shortened link, creates client (user) in DB if needed.

        """
        form = ShortenLinkForm(request.POST or None)
        context = {
            'form': form,
        }

        # Data for displaying users created short links
        base_url = request.build_absolute_uri('/l/')
        client_ip = get_client_ip(request)

        current_user_data = None
        try:
            # User exists, template can display his links
            current_user_data = Link.objects.filter(client__client_address=client_ip).select_related('client')
            context['current_user_data'] = current_user_data
        except Link.DoesNotExist:
            # User does not exist, he'll be created later, when he attempts to shorten link
            pass

        context['base_url'] = base_url

        # link shortening
        if form.is_valid():
            slug = random_sequence(10)

            # Try creating string not present already in db for input url 10 times
            attempt = 0
            while Link.objects.filter(url_output=slug).count() != 0:
                slug = random_sequence(10)
                if attempt > 10:
                    return HttpResponse("<h1>Failed to generate unique short link</h1>")  # todo: Use template here
                attempt += 1

            # check if user exists, create user if needed, check if he's allowed to shorten links
            requester_ip = get_client_ip(request)
            if not Client.objects.filter(client_address=requester_ip).exists():
                selected_client = Client(client_address=requester_ip)
                selected_client.save()

            else:
                selected_client = Client.objects.get(client_address=requester_ip)

                # check if user is allowed to shorten links and return page with error if needed
                if selected_client.is_banned is True:
                    context['shortening_error'] = "You are banned from shortening links!"
                    return render(request, 'ShortenerIndex/index.html', context=context, status=403)
                if selected_client.urls_count >= 5:
                    context['shortening_error'] = "You have reached 5 shortened links limit. " \
                                                 "Remove at least one of your old links and try again!"
                    return render(request, 'ShortenerIndex/index.html', context=context, status=403)

                selected_client.urls_count += 1
                selected_client.save()

            url = form.cleaned_data["url_input"]
            new_url = Link(url_input=url, url_output=slug, client=selected_client)
            new_url.save()

            # Pass info on users links, so they can be displayed in template
            current_user_data = Link.objects.filter(client__client_address=client_ip).select_related('client')
            context['current_user_data'] = current_user_data

            # Full url leading to shortened link
            shortened_url = request.build_absolute_uri('/l/' + slug)

            # This will be displayed in the template as a result
            context['short_url'] = shortened_url

        return render(request, 'ShortenerIndex/index.html', context=context)


class RedirectView(View):
    """
    Redirect to external website using slug argument
    """
    # Redirects user to proper URL using shortened link
    def get(self, request, url_output):
        data = Link.objects.filter(url_output=url_output).first()

        # Without this check, django could redirect user to subpage of our page in some cases
        if data.url_input.startswith("http"):
            return HttpResponseRedirect(data.url_input)
        return HttpResponseRedirect("http://" + data.url_input)

    # Used for deletion of specific link, and lowering link count for specific user
    def post(self, request, url_output):

        client_ip = get_client_ip(request)
        current_user_data = Link.objects.select_related('client').get(url_output=url_output)

        current_link = Link.objects.get(url_output=url_output)
        current_user = Client.objects.get(client_address=current_user_data.client.client_address)

        if current_user_data.client.client_address == client_ip:
            current_user.urls_count -= 1
            current_user.save()
            current_link.delete()
            return HttpResponseRedirect(reverse('index'))
        else:
            return HttpResponseForbidden()
