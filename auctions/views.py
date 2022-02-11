from uuid import UUID
import uuid
from django.contrib.auth import authenticate, login, logout
from django.core.checks import messages
from django.db import IntegrityError
from django.db.models.fields import UUIDField
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
import datetime

from auctions.verify import check_bid_count, user_by_user, get_max_bid
from .models import User, Listings, Bids, Comments, Watchlist
from django.contrib.auth.decorators import login_required
from django.db.models import Max
from django.core.exceptions import ObjectDoesNotExist


def index(request):
    return render(request, "auctions/index.html", {
        "listings": list(Listings.objects.values_list())
    })


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "auctions/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "auctions/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")


def create_listing(request):
    if request.method == "POST":
        name = request.POST["title"]
        description = request.POST["description"]
        bid = request.POST["bid"]
        image = request.POST["image_url"]
        category = request.POST["category"]
        user = request.user.username

        try:
            listing = Listings.objects.create(
                name=name,
                price=bid,
                description=description,
                create_date=datetime.datetime.now(),
                listed_by=user,
                category=category,
                photo=image)
        except IntegrityError:
            return(request, "auctions/create_listing.html", {
                "message": "Oh..."
            })
    return render(request, "auctions/create_listing.html")


def listing(request, id):
    product = Listings.objects.get(pk=id)
    product_comments = Comments.objects.filter(product=id)
    if request.user.is_anonymous:
        is_watchlist = False
    else:
        # TODO: bug
        is_watchlist = Watchlist.objects.filter(
            user=request.user, item=id).exists()

    if product.__dict__["status"] == 1:
        win_user = product.__dict__["winner"]
        winner_bid = product.__dict__["win_bid"]
    else:
        win_user = None
        winner_bid = None

    return render(request, "auctions/listing.html", {
        "username": request.user.username,
        "name": product.__dict__["name"],
        "description": product.__dict__["description"],
        "price": product.__dict__["price"],
        "user_by": product.__dict__["listed_by"],
        "category": product.__dict__["category"],
        "create_date": product.__dict__["create_date"],
        "image_url": product.__dict__["photo"],
        "id": product.__dict__["id"],
        "message": None,
        "watchlist": is_watchlist,
        "count_bids": len(list(Bids.objects.filter(
            product=product.__dict__['id']).values_list("bid_price", flat=True))),
        "winner": win_user,
        "win_price": winner_bid,
        "comments": product_comments.values_list()
    })


@login_required
def watchlist_add(request, id):
    product = Listings.objects.get(pk=id)
    item_to_save = get_object_or_404(Listings, pk=id)
    product_comments = Comments.objects.filter(product=id)
    # delete
    if Watchlist.objects.filter(user=request.user, item=id).exists():
        user_list, created = Watchlist.objects.filter(user=request.user, item=id).delete()
        # TODO: update db for watchlist page
        return render(request, "auctions/listing.html", {
            "username": request.user.username,
            "name": product.__dict__["name"],
            "description": product.__dict__["description"],
            "price": product.__dict__["price"],
            "user_by": product.__dict__["listed_by"],
            "category": product.__dict__["category"],
            "create_date": product.__dict__["create_date"],
            "image_url": product.__dict__["photo"],
            "id": product.__dict__["id"],
            "message": "Product has been remove to watchlist",
            "watchlist": Watchlist.objects.filter(user=request.user, item=id).exists(),
            "count_bids": len(list(Bids.objects.filter(
                product=product.__dict__['id']).values_list("bid_price", flat=True))),
            "comments": product_comments.values_list()
        })
    else:
        print('item_to_save', item_to_save.id)
        user_list, created = Watchlist.objects.get_or_create(user=request.user, item=item_to_save.id)
        # user_list.item.add(item_to_save)
    return render(request, "auctions/listing.html", {
        "username": request.user.username,
        "name": product.__dict__["name"],
        "description": product.__dict__["description"],
        "price": product.__dict__["price"],
        "user_by": product.__dict__["listed_by"],
        "category": product.__dict__["category"],
        "create_date": product.__dict__["create_date"],
        "image_url": product.__dict__["photo"],
        "id": product.__dict__["id"],
        "message": "Product has been added to watchlist",
        "watchlist": Watchlist.objects.filter(user=request.user, item=id).exists(),
        "count_bids": len(list(Bids.objects.filter(
            product=product.__dict__['id']).values_list("bid_price", flat=True))),
        "comments": product_comments.values_list()
    })


def add_bid(request, id):
    product = Listings.objects.get(pk=id)
    product_comments = Comments.objects.filter(product=id)

    if user_by_user(product.__dict__["listed_by"], request.user.username):
        message = "User who created the auction cannot place bids"
    elif check_bid_count(
            request.POST["bid"],
            product.__dict__["price"]) and check_bid_count(
                request.POST["bid"],
                get_max_bid(list(Bids.objects.filter(
            product=product.__dict__['id']).values_list("bid_price", flat=True)))):
        message = "Bid accepted"
        bid = Bids.objects.create(
            bid_price=request.POST["bid"],
            create_date=datetime.datetime.now(),
            product=int(product.__dict__["id"]),
            user_by=request.user
        )
    else:
        message = "Bid must be higher"
    return render(request, "auctions/listing.html", {
        "username": request.user.username,
        "name": product.__dict__["name"],
        "description": product.__dict__["description"],
        "price": product.__dict__["price"],
        "user_by": product.__dict__["listed_by"],
        "category": product.__dict__["category"],
        "create_date": product.__dict__["create_date"],
        "image_url": product.__dict__["photo"],
        "id": product.__dict__["id"],
        "message": message,
        "watchlist": Watchlist.objects.filter(user=request.user, item=id).exists(),
        "count_bids": len(list(Bids.objects.filter(
            product=product.__dict__['id']).values_list("bid_price", flat=True))),
        "comments": product_comments.values_list()
    })

def close(request, id):
    product = Listings.objects.get(pk=id)

    product_bids = Bids.objects.filter(product=id)
    winner_bid = product_bids.filter().aggregate(Max('bid_price'))['bid_price__max']

    try: 
        Listings.objects.filter(id=id).update(
            status=True,
            winner=Bids.objects.get(bid_price=winner_bid).user_by,
            win_bid=winner_bid
        )
        product_comments = Comments.objects.filter(product=id)
        win_user = Bids.objects.get(bid_price=winner_bid).user_by
        message = "Listing was close. Winner: {0}, price: {1}".format(
            win_user, winner_bid)
    except ObjectDoesNotExist:
        message = "No bids"

    return render(request, "auctions/listing.html", {
        "username": request.user.username,
        "name": product.__dict__["name"],
        "description": product.__dict__["description"],
        "price": product.__dict__["price"],
        "user_by": product.__dict__["listed_by"],
        "category": product.__dict__["category"],
        "create_date": product.__dict__["create_date"],
        "image_url": product.__dict__["photo"],
        "id": product.__dict__["id"],
        "message": message,
        "watchlist": Watchlist.objects.filter(user=request.user, item=id).exists(),
        "count_bids": len(list(Bids.objects.filter(
            product=product.__dict__['id']).values_list("bid_price", flat=True))),
        "comments": product_comments.values_list()
    })

@login_required
def comments(request, id):
    product = Listings.objects.get(pk=id)

    if request.method == "POST":
        Comments.objects.create(
            comment=request.POST["comment"],
            user_by=request.user.username,
            date=datetime.datetime.now(),
            product=Listings.objects.get(pk=id).id
        )
    comment = request.POST["comment"]

    product_comments = Comments.objects.filter(product=id)
    return render(request, "auctions/listing.html", {
        "username": request.user.username,
        "name": product.__dict__["name"],
        "description": product.__dict__["description"],
        "price": product.__dict__["price"],
        "user_by": product.__dict__["listed_by"],
        "category": product.__dict__["category"],
        "create_date": product.__dict__["create_date"],
        "image_url": product.__dict__["photo"],
        "id": product.__dict__["id"],
        "message": None,
        "watchlist": Watchlist.objects.filter(user=request.user, item=id).exists(),
        "count_bids": len(list(Bids.objects.filter(
            product=product.__dict__['id']).values_list("bid_price", flat=True))),
        "comments": product_comments.values_list()
    })

def categories(request):
    categories = Listings.objects.values_list('category')
    print(list(categories))
    return render(request, "auctions/categories.html", {
        "categories": categories.distinct()
    })
    

def category(request, category):
    products = Listings.objects.filter(category=category)
    return render(request, "auctions/index.html", {
        "listings": list(products.values_list())
    })


def watchlist(request, user_id):
    user_id = request.user.username
    watch = Watchlist.objects.filter(user=user_id)

    print('watch', watch.values_list())

    user_watchlist = []
    
    print('watch', watch)
    print('user_watchlist', user_watchlist)
    
    for i in watch.values_list():
        print('lolkek', Listings.objects.filter(id=i[2]).values_list())
        # user_watchlist += Watchlist.objects.filter(item=i[2]).values_list()
        user_watchlist += Listings.objects.filter(id=i[2]).values_list()

    print('user_watchlist', user_watchlist)
    return render(request, "auctions/index.html", {
        "listings": list(user_watchlist)
    })

# TODO: watchlist logic (add/delete and view)
# TODO: watchlist count
