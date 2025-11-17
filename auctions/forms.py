# auctions/forms.py

from django import forms
from .models import Product


class ProductForm(forms.ModelForm):
    """
    Form used by users/admins to create a product.
    - Users can choose if it's Buy Now or Auction (BID).
    - For auctions we enforce starting_bid, min_increment and auction_end.
    """

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
        ]
        widgets = {
            "title": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Product title",
                }
            ),
            "description": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 4,
                    "placeholder": "Describe your product…",
                }
            ),
            "image": forms.ClearableFileInput(
                attrs={"class": "form-control"}
            ),
            "listing_type": forms.Select(
                attrs={"class": "form-control"}
            ),
            "price": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "step": "0.01",
                    "placeholder": "Buy Now price (Rs.)",
                }
            ),
            "starting_bid": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "step": "0.01",
                    "placeholder": "Starting bid (for auctions)",
                }
            ),
            "min_increment": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "step": "0.01",
                    "placeholder": "Minimum increment (for auctions)",
                }
            ),
            "auction_end": forms.DateTimeInput(
                attrs={
                    "class": "form-control",
                    "type": "datetime-local",
                }
            ),
        }

    def clean(self):
        """
        Extra validation:
        - If listing_type == 'BID', require starting_bid, min_increment, auction_end.
        """
        cleaned = super().clean()
        listing_type = cleaned.get("listing_type")
        starting_bid = cleaned.get("starting_bid")
        min_increment = cleaned.get("min_increment")
        auction_end = cleaned.get("auction_end")

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
            if auction_end is None:
                self.add_error(
                    "auction_end",
                    "End date/time is required for auction listings.",
                )

        return cleaned
