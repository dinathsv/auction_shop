from django.urls import path
from . import views

app_name = "auctions"

urlpatterns = [
    path("", views.auction_list, name="listing_list"),
    path("<int:pk>/", views.auction_detail, name="listing_detail"),
    path("<int:pk>/bid/", views.place_bid, name="place_bid"),
    path("<int:pk>/buy-now/", views.buy_now, name="buy_now"),

    path("product/add/", views.product_create, name="product_add"),
    path("<int:pk>/status/", views.product_status_json, name="status_json"),

    # NEW
    path("<int:pk>/watch/", views.toggle_watchlist, name="toggle_watchlist"),
    path("watchlist/", views.my_watchlist, name="watchlist"),
    path("dashboard/", views.my_dashboard, name="dashboard"),
    path("product/<int:pk>/edit/", views.product_edit, name="product_edit"),
    path("product/<int:pk>/delete/", views.product_delete, name="product_delete"),


]
