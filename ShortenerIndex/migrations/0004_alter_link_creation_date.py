# Generated by Django 3.2.5 on 2021-09-07 14:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ShortenerIndex', '0003_alter_link_creation_date'),
    ]

    operations = [
        migrations.AlterField(
            model_name='link',
            name='creation_date',
            field=models.DateTimeField(default='07.09.2021 14:10'),
        ),
    ]
