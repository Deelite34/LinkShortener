from django.conf import settings


def default_domain(request):
    return {'default_domain': settings.DEFAULT_DOMAIN}
