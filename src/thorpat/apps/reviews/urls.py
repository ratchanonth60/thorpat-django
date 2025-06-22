from django.urls import path

from .views import AddProductReviewView

app_name = "reviews"

urlpatterns = [
    path("add/", AddProductReviewView.as_view(), name="add_review"),
]
