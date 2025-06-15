from django.shortcuts import get_object_or_404
from django.views.generic import DetailView, ListView

from thorpat.apps.cart.forms import AddToCartForm

from .models import Product, ProductCategory


class ProductListView(ListView):
    """
    A view to display a list of products, optionally filtered by category.
    """

    model = Product
    template_name = "catalogue/product_list.html"
    context_object_name = "products"
    paginate_by = 12  # Show 12 products per page

    def get_queryset(self):
        queryset = Product.objects.filter(is_public=True, user=self.request.user)
        category_slug = self.kwargs.get("category_slug")
        if category_slug:
            self.category = get_object_or_404(ProductCategory, slug=category_slug)
            queryset = queryset.filter(categories=self.category)
        else:
            self.category = None
        return queryset.order_by("-created_at")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["category"] = self.category
        context["categories"] = ProductCategory.objects.all()
        return context


class ProductDetailView(DetailView):
    """
    A view to display the details of a single product.
    """

    model = Product
    template_name = "catalogue/product_detail.html"
    context_object_name = "product"
    slug_field = "slug"
    slug_url_kwarg = "slug"

    def get_queryset(self):
        # Ensure we only show public products
        return Product.objects.filter(is_public=True)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Add the 'Add to Cart' form to the context
        context["add_to_cart_form"] = AddToCartForm()
        return context
