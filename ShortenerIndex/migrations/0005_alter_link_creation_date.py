# Generated by Django 3.2.5 on 2021-09-08 17:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ShortenerIndex', '0004_alter_link_creation_date'),
    ]

    operations = [
        migrations.AlterField(
            model_name='link',
            name='creation_date',
            field=models.DateTimeField(auto_now_add=True),
        ),
    ]
