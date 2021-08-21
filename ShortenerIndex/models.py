import datetime
import pytz

from django.db import models
from django.core.validators import RegexValidator
# Create your models here.


class Client(models.Model):
    urls_count = models.IntegerField(blank=True, default=1)
    client_address = models.CharField(max_length=15, blank=True)
    is_banned = models.BooleanField(default=False)

    def __str__(self):
        return f"user-{self.id}"


class Link(models.Model):
    # Only signs needed for creating URL are allowed
    alphabetic = RegexValidator(regex=r'^[a-zA-Z:/.]*$',
                                message='Only alphabetic and: ":", "/", "." ' +
                                        'characters are allowed in URL to shorten.')

    client = models.ForeignKey(Client, on_delete=models.CASCADE)
    url_input = models.CharField(max_length=255, validators=[alphabetic])
    url_output = models.CharField(max_length=255, unique=True, blank=True)
    duration = models.IntegerField(blank=True, null=True)
    creation_date = models.DateTimeField(auto_now=True)
    expiration_date = models.DateTimeField(blank=True,
                                           default=datetime.datetime(2055, 12, 12,
                                                                     tzinfo=pytz.timezone('Europe/Berlin')))

    def __str__(self):
        return f"{self.url_input} ({self.id})"
