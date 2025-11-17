# auctions/models.py

from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class Category(models.Model):
    name = models.CharField(max_length=80, unique=True)
    slug = models.SlugField(max_length=100, unique=True)

    class Meta:
        verbose_name_plural = "categories"
        ordering = ["name"]

    def __str__(self):
        return self.name


class Product(models.Model):
    LISTING_TYPE_CHOICES = [
        ("BUY", "Buy Now"),
        ("BID", "Auction (Bidding)"),
    ]

    seller = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="products",
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="products",
    )

    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to="products/", blank=True, null=True)

    listing_type = models.CharField(
        max_length=3,
        choices=LISTING_TYPE_CHOICES,
        default="BUY",
    )

    # Buy-now price (also used as reference for orders)
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text="Buy Now price",
    )

    # Auction-only fields
    starting_bid = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        blank=True,
        null=True,
    )
    min_increment = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        blank=True,
        null=True,
        help_text="Minimum amount above current bid",
    )
    auction_end = models.DateTimeField(
        blank=True,
        null=True,
        help_text="End time for auction listings",
    )

    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    # Winner / closing info for auctions
    winner = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="won_auctions",
    )
    closed_at = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return self.title

    # ---------- Helpers ----------

    @property
    def is_auction(self) -> bool:
        return self.listing_type == "BID"

    @property
    def highest_bid_obj(self):
        if not self.is_auction:
            return None
        return self.bids.order_by("-amount", "-created_at").first()

    @property
    def highest_bid(self):
        if not self.is_auction:
            return None
        top = self.highest_bid_obj
        return top.amount if top else self.starting_bid

    @property
    def time_left_seconds(self):
        if not self.auction_end:
            return None
        delta = self.auction_end - timezone.now()
        return max(int(delta.total_seconds()), 0)

    def close_if_finished(self):
        """
        If auction end time passed, close auction and set winner.
        Safe to call multiple times.
        """
        if not self.is_auction or not self.auction_end:
            return

        if self.is_active and timezone.now() >= self.auction_end:
            top_bid = self.highest_bid_obj
            if top_bid:
                self.winner = top_bid.bidder
            self.is_active = False
            self.closed_at = timezone.now()
            self.save()


class Bid(models.Model):
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="bids",
        null=True,   # keep nullable to avoid migration pain on old rows
        blank=True,
    )
    bidder = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="bids",
    )
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.bidder.username} → {self.product} ({self.amount})"


class Watchlist(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="watchlist_items",
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="watchlisted_by",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "product")

    def __str__(self):
        return f"{self.user.username} → {self.product.title}"


class Order(models.Model):
    STATUS_CHOICES = [
        ("PENDING", "Pending"),
        ("COMPLETED", "Completed"),
        ("CANCELLED", "Cancelled"),
    ]

    buyer = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="orders",
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.PROTECT,
        related_name="orders",
    )
    price = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default="PENDING",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Order #{self.pk} - {self.product.title}"
