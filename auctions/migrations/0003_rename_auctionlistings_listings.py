# Generated by Django 3.2.9 on 2021-12-07 17:18

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('auctions', '0002_auctionlistings_bids_comments'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='AuctionListings',
            new_name='Listings',
        ),
    ]
