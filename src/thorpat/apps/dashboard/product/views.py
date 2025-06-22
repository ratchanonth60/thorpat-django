from django.http import HttpResponseRedirect
from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, ListView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin

from thorpat.apps.catalogue.forms import ProductForm, StockRecordFormSet
from thorpat.apps.catalogue.models import Product, StockRecord


class ProductListView(LoginRequiredMixin, ListView):
    model = Product
    template_name = "dashboard/product/list.html"
    context_object_name = "products"

    def get_queryset(self):
        return Product.objects.filter(user=self.request.user)


class ProductCreateView(LoginRequiredMixin, CreateView):
    model = Product
    form_class = ProductForm
    template_name = "dashboard/product/form.html"
    success_url = reverse_lazy("dashboard:products:list")

    def get_form_kwargs(self):
        """Pass the user to the form."""
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs

    def get_context_data(self, **kwargs):
        """
        Add the stockrecord formset to the context.
        """
        context = super().get_context_data(**kwargs)
        if "stockrecord_formset" not in context:
            context["stockrecord_formset"] = StockRecordFormSet(
                self.request.POST or None, form_kwargs={"user": self.request.user}
            )
        return context

    def post(self, request, *args, **kwargs):
        """
        Handle POST requests, instantiating a form instance and a
        formset instance with the passed POST variables and then checking them
        for validity.
        """
        self.object = None
        form = self.get_form()
        formset = StockRecordFormSet(request.POST, form_kwargs={"user": request.user})

        if form.is_valid() and formset.is_valid():
            return self.form_valid(form, formset)
        else:
            return self.form_invalid(form, formset)

    def form_valid(self, form, formset):
        """
        If the forms are valid, save the associated models.
        """
        self.object = form.save(commit=False)
        self.object.user = self.request.user
        self.object.save()

        formset.instance = self.object
        formset.save()

        return HttpResponseRedirect(self.get_success_url())

    def form_invalid(self, form, formset):
        """
        If the forms are invalid, re-render the context data with the
        data-filled forms and errors.
        """
        return self.render_to_response(
            self.get_context_data(form=form, stockrecord_formset=formset)
        )


class ProductUpdateView(LoginRequiredMixin, UpdateView):
    model = Product
    form_class = ProductForm
    template_name = "dashboard/product/form.html"
    success_url = reverse_lazy("dashboard:products:list")

    def get_queryset(self):
        return Product.objects.filter(user=self.request.user)

    def get_form_kwargs(self):
        """Pass the user to the form."""
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if "stockrecord_formset" not in context:
            context["stockrecord_formset"] = StockRecordFormSet(
                instance=self.object, form_kwargs={"user": self.request.user}
            )
        return context

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        form = self.get_form()
        formset = StockRecordFormSet(
            request.POST, instance=self.object, form_kwargs={"user": request.user}
        )
        if form.is_valid() and formset.is_valid():
            form.save()
            formset.save()
            return HttpResponseRedirect(self.get_success_url())
        else:
            return self.render_to_response(
                self.get_context_data(form=form, stockrecord_formset=formset)
            )


class ProductDeleteView(LoginRequiredMixin, DeleteView):
    model = Product
    template_name = "dashboard/product/confirm_delete.html"
    success_url = reverse_lazy("dashboard:products:list")

    def get_queryset(self):
        return Product.objects.filter(user=self.request.user)

