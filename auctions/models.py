import uuid
from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    pass
    # 1. read docs https://docs.djangoproject.com/en/3.2/topics/db/models/
    # 2. watch lecture

    # one for auction listings -> str
    # bids -> num
    # and one for comments made on auction listings -> str

    # make migrate


class Listings(models.Model):
    name = models.CharField(max_length=30)
    price = models.FloatField(max_length=30)
    description = models.CharField(max_length=100)
    create_date = models.DateField(max_length=30)
    listed_by = models.CharField(max_length=30)
    category = models.CharField(max_length=30)
    photo = models.CharField(max_length=500, default='')
    status = models.BooleanField(default=False)
    winner = models.CharField(max_length=30, default='')
    win_bid = models.FloatField(max_length=30, default=0)


class Bids(models.Model):
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    bid_price = models.FloatField(max_length=30)
    product = models.IntegerField(max_length=30)
    create_date = models.DateField(max_length=30)
    user_by = models.CharField(max_length=30)


class Comments(models.Model):
    comment = models.CharField(max_length=100)
    user_by = models.CharField(max_length=30)
    date = models.DateField(max_length=30)
    product = models.CharField(max_length=30)


class Watchlist(models.Model):
    # TODO: bug
    user = models.CharField(max_length=30)
    item = models.IntegerField(max_length=30, default=0)
