from django import forms

from .models import ProductReview


class ProductReviewForm(forms.ModelForm):
    class Meta:
        model = ProductReview
        fields = ["rating", "title", "body"]
        widgets = {
            "rating": forms.Select(attrs={"class": "select select-bordered w-full"}),
            "title": forms.TextInput(
                attrs={
                    "class": "input input-bordered w-full",
                    "placeholder": "e.g., Excellent quality!",
                }
            ),
            "body": forms.Textarea(
                attrs={
                    "class": "textarea textarea-bordered w-full",
                    "rows": 4,
                    "placeholder": "Write your detailed review here...",
                }
            ),
        }
