# Generated by Django 3.2.5 on 2021-09-07 13:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ShortenerIndex', '0002_alter_client_urls_count'),
    ]

    operations = [
        migrations.AlterField(
            model_name='link',
            name='creation_date',
            field=models.DateTimeField(auto_now_add=True),
        ),
    ]