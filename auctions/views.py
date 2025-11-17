# auctions/views.py

from decimal import Decimal
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect
from django.utils import timezone
from .forms import ProductForm
from .models import Product, Bid, Watchlist, Order
from django.shortcuts import render


# =========================
# LIST & DETAIL VIEWS
# =========================

@login_required
def my_dashboard(request):
    """
    Simple dashboard for the logged-in user:
    - Products they are selling
    - Their bids
    - Their watchlist items
    - Their orders
    """
    user = request.user

    selling = (
        Product.objects
        .filter(seller=user)
        .order_by("-created_at")
    )

    my_bids = (
        Bid.objects
        .filter(bidder=user)
        .select_related("product")
        .order_by("-created_at")[:20]
    )

    watch_items = (
        Watchlist.objects
        .filter(user=user)
        .select_related("product", "product__seller")
        .order_by("-created_at")
    )

    orders = (
        Order.objects
        .filter(buyer=user)
        .select_related("product")
        .order_by("-created_at")
    )

    # small stats
    now = timezone.now()
    active_auctions = selling.filter(listing_type="BID", is_active=True).count()
    active_buy_now = selling.filter(listing_type="BUY", is_active=True).count()

    context = {
        "selling": selling,
        "my_bids": my_bids,
        "watch_items": watch_items,
        "orders": orders,
        "active_auctions": active_auctions,
        "active_buy_now": active_buy_now,
        "now": now,
    }
    return render(request, "auctions/dashboard.html", context)

def auction_list(request):
    """
    Show all active products (both Buy Now & Auction).
    """
    products = (
        Product.objects.filter(is_active=True)
        .select_related("seller", "category")
        .order_by("-created_at")
    )
    return render(
        request,
        "auctions/listing_list.html",
        {"products": products},
    )


def auction_detail(request, pk):
    """
    Detail page for a single product (auction or buy-now).
    Includes bids and watchlist info.
    """
    product = get_object_or_404(Product, pk=pk)

    # auto-close auction if time ended
    product.close_if_finished()

    bids = (
        product.bids.order_by("-amount", "-created_at")
        if product.is_auction
        else []
    )

    is_watching = False
    if request.user.is_authenticated:
        is_watching = Watchlist.objects.filter(
            user=request.user, product=product
        ).exists()

    context = {
        "product": product,
        "bids": bids,
        "is_watching": is_watching,
    }
    return render(request, "auctions/listing_detail.html", context)


# =========================
# CREATE PRODUCT
# =========================

@login_required
def product_create(request):
    """
    Let any logged-in user create a product (admin can manage via admin site).
    """
    if request.method == "POST":
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save(commit=False)
            product.seller = request.user
            product.save()
            messages.success(request, "Product created successfully.")
            return redirect("auctions:listing_detail", pk=product.pk)
    else:
        form = ProductForm()

    return render(
        request,
        "auctions/product_form.html",
        {"form": form},
    )


# =========================
# BIDDING
# =========================

@login_required
def place_bid(request, pk):
    """
    Place a bid on an active auction.
    """
    product = get_object_or_404(
        Product,
        pk=pk,
        listing_type="BID",
        is_active=True,
    )

    # refresh status if auction passed its end time
    product.close_if_finished()
    if not product.is_active:
        messages.error(request, "This auction has already ended.")
        return redirect("auctions:listing_detail", pk=product.pk)

    if request.method == "POST":
        try:
            amount = Decimal(request.POST.get("amount", "0"))
        except Exception:
            messages.error(request, "Invalid bid amount.")
            return redirect("auctions:listing_detail", pk=product.pk)

        # minimum allowed = highest bid + min_increment (or starting_bid)
        min_allowed = product.starting_bid or Decimal("0")
        current_top = product.highest_bid
        if current_top is not None:
            increment = product.min_increment or Decimal("1.00")
            min_allowed = current_top + increment

        if amount < min_allowed:
            messages.error(
                request,
                f"Your bid must be at least {min_allowed}.",
            )
        else:
            Bid.objects.create(
                product=product,
                bidder=request.user,
                amount=amount,
            )
            messages.success(request, "Bid placed successfully!")

    return redirect("auctions:listing_detail", pk=product.pk)


# =========================
# BUY NOW
# =========================

@login_required
def buy_now(request, pk):
    """
    Simple 'buy now' flow:
      - create an Order
      - mark product inactive
      - set winner for auctions
    """
    product = get_object_or_404(
        Product,
        pk=pk,
        is_active=True,
    )

    if request.method == "POST":
        # close auction if needed
        product.close_if_finished()

        if not product.is_active:
            messages.error(request, "This listing is no longer available.")
            return redirect("auctions:listing_detail", pk=product.pk)

        Order.objects.create(
            buyer=request.user,
            product=product,
            price=product.price,
            status="COMPLETED",
        )

        # Mark product inactive and, if auction, set winner.
        product.is_active = False
        if product.is_auction:
            product.winner = request.user
            product.closed_at = timezone.now()
        product.save()

        messages.success(request, "You purchased this item (demo order).")
        return redirect("auctions:listing_detail", pk=product.pk)

    # GET -> just redirect back
    return redirect("auctions:listing_detail", pk=product.pk)


# =========================
# WATCHLIST TOGGLE
# =========================

@login_required
def toggle_watchlist(request, pk):
    """
    Add or remove a product from the user's watchlist.
    """
    product = get_object_or_404(Product, pk=pk)

    watch_item, created = Watchlist.objects.get_or_create(
        user=request.user,
        product=product,
    )

    if not created:
        # already there -> remove
        watch_item.delete()
        messages.info(request, "Removed from your watchlist.")
    else:
        messages.success(request, "Added to your watchlist.")

    return redirect("auctions:listing_detail", pk=product.pk)


# =========================
# STATUS JSON (for AJAX / polling)
# =========================

def product_status_json(request, pk):
    """
    Small JSON endpoint with live status.
    Can be used later by JS polling if you want.
    """
    product = get_object_or_404(Product, pk=pk)
    product.close_if_finished()

    highest = product.highest_bid
    data = {
        "id": product.pk,
        "is_active": product.is_active,
        "is_auction": product.is_auction,
        "highest_bid": str(highest) if highest is not None else None,
        "time_left": product.time_left_seconds,
        "winner": product.winner.username if product.winner else None,
    }
    return JsonResponse(data)

@login_required
def my_watchlist(request):
    """
    Show all products the current user has added to their watchlist.
    """
    items = (
        Watchlist.objects
        .filter(user=request.user)
        .select_related("product", "product__seller")
        .order_by("-created_at")
    )

    return render(
        request,
        "auctions/watchlist.html",
        {"items": items},
    )

@login_required
def product_edit(request, pk):
    """
    Edit an existing product.
    Only the seller or a staff user can edit.
    """
    product = get_object_or_404(Product, pk=pk)

    # only owner or admin can edit
    if not (request.user == product.seller or request.user.is_staff):
        messages.error(request, "You are not allowed to edit this product.")
        return redirect("auctions:listing_detail", pk=product.pk)

    if request.method == "POST":
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            obj = form.save(commit=False)
            # keep the original seller
            obj.seller = product.seller
            obj.save()
            messages.success(request, "Product updated successfully.")
            return redirect("auctions:listing_detail", pk=obj.pk)
    else:
        form = ProductForm(instance=product)

    return render(
        request,
        "auctions/product_form.html",
        {"form": form, "product": product},
    )

@login_required
def product_delete(request, pk):
    """
    Delete an existing product.
    Only the seller or a staff user can delete.
    """
    product = get_object_or_404(Product, pk=pk)

    # only owner or admin can delete
    if not (request.user == product.seller or request.user.is_staff):
        messages.error(request, "You are not allowed to delete this product.")
        return redirect("auctions:listing_detail", pk=product.pk)

    if request.method == "POST":
        title = product.title
        product.delete()
        messages.success(request, f'"{title}" was deleted.')
        return redirect("auctions:listing_list")

    # GET: show confirmation page
    return render(
        request,
        "auctions/product_confirm_delete.html",
        {"product": product},
    )
