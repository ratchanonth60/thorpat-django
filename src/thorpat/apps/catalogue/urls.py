from django.urls import path

from . import views

app_name = "catalogue"

urlpatterns = [
    # Example: /products/
    path("", views.ProductListView.as_view(), name="product_list"),
    # Example: /products/category/t-shirts/
    path(
        "category/<slug:category_slug>/",
        views.ProductListView.as_view(),
        name="product_list_by_category",
    ),
    path("<slug:slug>/", views.ProductDetailView.as_view(), name="product_detail"),
]
