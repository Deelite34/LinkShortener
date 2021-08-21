from django.contrib import admin
from .models import Link, Client

# Register your models here.

@admin.display(description='Client ID')
def client_id_display(object):
    return f"{object.client.id}"

# TODO: when you delete link on admin page, that user's link count should decrease by 1
class LinkAdmin(admin.ModelAdmin):
    list_display = ('id', client_id_display, 'url_input', 'url_output', 'duration', 'creation_date', 'expiration_date')


class ClientAdmin(admin.ModelAdmin):
    list_display = ('id', 'urls_count', 'client_address', 'is_banned')


admin.site.register(Link, LinkAdmin)
admin.site.register(Client, ClientAdmin)
