from django.db import transaction

from thorpat.apps.cart.models import Cart
from thorpat.apps.catalogue.models import StockRecord
from thorpat.apps.profiles.models import Address as ProfileAddress

from .models import BillingAddress, Order, OrderLine, ShippingAddress


class OrderPlacementError(Exception):
    """Custom exception for order placement errors."""

    pass


class OrderCreator:
    """
    Handles the creation of an order from a cart.
    """

    def place_order(
        self,
        cart: Cart,
        user,
        shipping_address: ProfileAddress,
        billing_address: ProfileAddress = None,
    ) -> Order:
        """
        Main method to place an order.
        """
        if cart.is_empty:
            raise OrderPlacementError("Cannot place an order with an empty cart.")

        if not billing_address:
            billing_address = shipping_address

        with transaction.atomic():
            # 1. Freeze the cart to prevent further modifications
            cart.status = Cart.SUBMITTED
            cart.save()

            # 2. Create snapshot addresses for the order
            order_shipping_address = self._create_shipping_address(shipping_address)
            order_billing_address = self._create_billing_address(billing_address)

            # 3. Create the main Order object
            order = self._create_order(
                cart=cart,
                user=user,
                shipping_address=order_shipping_address,
                billing_address=order_billing_address,
            )

            # 4. Create OrderLine items from cart lines
            for line in cart.lines.all():
                self._create_order_line(order=order, line=line)
                # 5. Decrement stock
                self._decrement_stock(line)

        # 6. (Optional) Send confirmation email, clear session data, etc.
        # This can be done in the view after the order is successfully placed.

        return order

    def _create_shipping_address(self, address_data: ProfileAddress) -> ShippingAddress:
        shipping_addr = ShippingAddress()
        shipping_addr.populate_from_profile_address(address_data)
        shipping_addr.save()
        return shipping_addr

    def _create_billing_address(self, address_data: ProfileAddress) -> BillingAddress:
        billing_addr = BillingAddress()
        billing_addr.populate_from_profile_address(address_data)
        billing_addr.save()
        return billing_addr

    def _create_order(self, cart, user, shipping_address, billing_address) -> Order:
        order = Order.objects.create(
            cart=cart,
            user=user,
            shipping_address=shipping_address,
            billing_address=billing_address,
            total_excl_tax=cart.total_excl_tax,
            status="Pending",  # Initial status
        )
        return order

    def _create_order_line(self, order, line):
        stockrecord = line.product.primary_stockrecord
        OrderLine.objects.create(
            order=order,
            product=line.product,
            product_title=line.product.title,
            partner_sku=stockrecord.partner_sku if stockrecord else "",
            quantity=line.quantity,
            price_excl_tax=line.price_excl_tax,
            line_price_excl_tax=line.line_price_excl_tax,
        )

    def _decrement_stock(self, line):
        try:
            stockrecord = StockRecord.objects.get(product=line.product)
            if stockrecord.net_stock_level < line.quantity:
                raise OrderPlacementError(f"Not enough stock for {line.product.title}")

            stockrecord.num_in_stock -= line.quantity
            stockrecord.save()
        except StockRecord.DoesNotExist:
            raise OrderPlacementError(
                f"Stock record not found for {line.product.title}"
            )
