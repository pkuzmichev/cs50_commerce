# Generated by Django 3.2.9 on 2022-01-27 13:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auctions', '0007_listings_winner'),
    ]

    operations = [
        migrations.AddField(
            model_name='listings',
            name='win_bid',
            field=models.FloatField(default=0, max_length=30),
        ),
    ]