from django.contrib.auth import authenticate, login, logout
from django.core.checks import messages
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
import datetime
from .models import User, Listings, Bids, Comments, Watchlist



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
        "watchlist": Watchlist.objects.filter(user=request.user, item=id).exists()
    })

def watchlist_add(request, id):
    product = Listings.objects.get(pk=id)
    item_to_save = get_object_or_404(Listings, pk=id)
    if Watchlist.objects.filter(user=request.user, item=id).exists():
        # delete
        user_list, created = Watchlist.objects.get_or_create(user=request.user)
        user_list.item.remove(item_to_save)
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
            "watchlist": Watchlist.objects.filter(user=request.user, item=id).exists()
        })
    user_list, created = Watchlist.objects.get_or_create(user=request.user)
    user_list.item.add(item_to_save)
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
        "message": "Product has been deleted to watchlist",
        "watchlist": Watchlist.objects.filter(user=request.user, item=id).exists()
    })
