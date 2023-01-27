# Generated by Django 3.2.13 on 2023-01-27 12:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='basket',
            name='size',
            field=models.SmallIntegerField(choices=[(0, 'XS'), (1, 'S'), (2, 'M'), (3, 'L'), (4, 'XL'), (5, 'XXL')], default=0),
        ),
    ]
