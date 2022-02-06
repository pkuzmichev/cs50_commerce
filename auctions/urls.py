from unicodedata import name
from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("create_listing", views.create_listing, name="create_listing"),
    path("listing/<int:id>", views.listing, name="listing"),
    path("watchlist_add/<int:id>", views.watchlist_add, name="watchlist_add"),
    path("add_bid/<int:id>", views.add_bid, name="add_bid"),
    path("close/<int:id>", views.close, name="close"),
    path("add_comment/<int:id>", views.comments, name="add_comment"),
    path("categories", views.categories, name="categories"),
    path("category/<slug:category>", views.category, name="category"),
    path("watchlist/<slug:user_id>", views.watchlist, name="watchlist")
]
