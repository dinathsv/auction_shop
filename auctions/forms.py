# auctions/forms.py

from django import forms
from .models import Product


class ProductForm(forms.ModelForm):
class Meta:
model = Product
fields = [
"title",
"description",
"image",
"listing_type",
"price",
"starting_bid",
"min_increment",
"auction_end",
"is_active",
]
widgets = {
"auction_end": forms.DateTimeInput(
attrs={"type": "datetime-local"}
)
}

def clean(self):
cleaned = super().clean()
listing_type = cleaned.get("listing_type")
starting_bid = cleaned.get("starting_bid")
min_increment = cleaned.get("min_increment")

# For auction listings, require starting_bid and min_increment
if listing_type == "BID":
if starting_bid is None:
self.add_error(
"starting_bid",
"Starting bid is required for auction listings.",
)
if min_increment is None:
self.add_error(
"min_increment",
"Minimum increment is required for auction listings.",
)
return cleaned
