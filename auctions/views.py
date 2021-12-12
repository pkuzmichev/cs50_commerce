from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
import datetime
from .models import User, Listings, Bids, Comments



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
        # print("CREATE LISTING", name, description, bid, image, category)
    return render(request, "auctions/create_listing.html")
