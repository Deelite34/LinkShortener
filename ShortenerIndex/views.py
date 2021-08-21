import random
import string

from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect
from django.views import View
from .forms import ShortenLinkForm
from .models import Link, Client


class IndexView(View):

    def get(self, request):
        form = ShortenLinkForm()
        context = {
            'form': form,
        }
        return render(request, 'ShortenerIndex/index.html', context=context)

    def post(self, request):
        form = ShortenLinkForm(request.POST or None)
        context = {
            'form': form,
        }

        # link shortening
        if form.is_valid():
            slug = ''.join(random.choice(string.ascii_letters) for x in range(10))  # todo: DRY(replace with function?)

            # Try creating string not present already in db for input url 10 times
            attempt = 0
            while Link.objects.filter(url_output=slug).count() != 0:
                slug = ''.join(random.choice(string.ascii_letters) for x in range(10))  # todo: DRY(replace with function?)
                if attempt > 10:
                    return HttpResponse("<h1>Failed to generate unique short link</h1>")  # todo: Use template here
                attempt += 1

            # check if user exists, create user if needed, check if he's allowed to shorten links
            requester_ip = get_client_ip(request) # todo: maybe it's better to use hash of ip instead of ip
            if not Client.objects.filter(client_address=requester_ip).exists():
                new_client = Client(client_address=requester_ip)
                new_client.save()
            else:
                existing_user = Client.objects.get(client_address=requester_ip)

                # check if user is allowed to shorten links and return page with error if needed
                if existing_user.is_banned is True:
                    context['shortening_error'] = "You are banned from shortening links!"
                    return render(request, 'ShortenerIndex/index.html', context=context)
                if existing_user.urls_count >= 5:
                    context['shortening_error'] = "You have reached 5 shortened links limit. " \
                                                 "Remove at least one of your old links and try again!"
                    return render(request, 'ShortenerIndex/index.html', context=context)

                existing_user.urls_count += 1
                existing_user.save()

            url = form.cleaned_data["url_input"]
            created_client = Client.objects.get(client_address=requester_ip)
            new_url = Link(url_input=url, url_output=slug, client=new_client)
            new_url.save()

            # Full url leading to shortened link
            shortened_url = request.build_absolute_uri('/l/' + slug)

            # This will be displayed in the template as a result
            context['short_url'] = shortened_url

            return render(request, 'ShortenerIndex/index.html', context=context)
        else:
            return render(request, 'ShortenerIndex/index.html', context=context)


class RedirectView(View):
    """
    Redirect to external website using slug argument
    """

    def get(self, request, url_output):

        data = Link.objects.filter(url_output=url_output).first()

        # Without this check, django could redirect user to subpage of our page in some cases
        if data.url_input.startswith("http"):
            return HttpResponseRedirect(data.url_input)
        return HttpResponseRedirect("http://" + data.url_input)


def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip
