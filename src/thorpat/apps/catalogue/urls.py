from django.urls import path

from . import views

app_name = "catalogue"

urlpatterns = [
    path("", views.ProductListView.as_view(), name="product_list"),
    path("htmx/", views.ProductListHTMXView.as_view(), name="product_list_htmx"),
    path(
        "category/<slug:category_slug>/",
        views.ProductListView.as_view(),
        name="product_list_by_category",
    ),
    path(
        "<slug:slug>/",
        views.ProductDetailView.as_view(),
        name="product_detail",
    ),
    # Example: /products/category/t-shirts/
]
