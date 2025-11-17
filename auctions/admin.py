# auctions/admin.py

from django.contrib import admin
from django.utils.html import format_html

from .models import Category, Product, Bid, Watchlist, Order


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "slug")
    search_fields = ("name",)
    prepopulated_fields = {"slug": ("name",)}


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "seller",
        "category",
        "listing_type",
        "price",
        "starting_bid",
        "min_increment",
        "auction_end",
        "is_active",
        "created_at",
        "preview",          # image preview column
    )
    list_filter = ("listing_type", "is_active", "category", "created_at")
    search_fields = ("title", "description", "seller__username")
    ordering = ("-created_at",)
    list_editable = ("is_active",)
    readonly_fields = ("created_at",)

    def preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" width="50" style="border-radius:4px;" />',
                obj.image.url,
            )
        return "No Image"

    preview.short_description = "Image"


@admin.register(Bid)
class BidAdmin(admin.ModelAdmin):
    list_display = ("product", "bidder", "amount", "created_at")
    list_filter = ("created_at",)
    search_fields = ("product__title", "bidder__username")
    ordering = ("-created_at",)


@admin.register(Watchlist)
class WatchlistAdmin(admin.ModelAdmin):
    list_display = ("user", "product", "created_at")
    list_filter = ("created_at",)
    search_fields = ("user__username", "product__title")
    ordering = ("-created_at",)


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("id", "buyer", "product", "price", "status", "created_at")
    list_filter = ("status", "created_at")
    search_fields = ("buyer__username", "product__title")
    ordering = ("-created_at",)
