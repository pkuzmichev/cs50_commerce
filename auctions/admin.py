from django.contrib import admin

from auctions.models import *

# Register your models here.
class ListingsAdmin(admin.ModelAdmin):
    name = ['name']

class CommentsAdmin(admin.ModelAdmin):
    name = ['comment']

class BidsAdmin(admin.ModelAdmin):
    name = ['bids']

admin.site.register(Listings, ListingsAdmin)
admin.site.register(Comments, CommentsAdmin)
admin.site.register(Bids, BidsAdmin)