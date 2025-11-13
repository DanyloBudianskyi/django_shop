from django.conf import settings
from main.models import Product

class Cart:
    def __init__(self, request):
        self.session = request.session
        cart = self.session.get(settings.CART_SESSION_ID)
        if not cart:
            cart = self.session[settings.CART_SESSION_ID] = {}

        self.cart = cart

        self.shipping_cost = self.session.get('shipping_cost', 100)
        self.free_shipping = self.session.get('free_shipping', False)
        self.discounted_total = self.session.get('discounted_total', None)

    def add(self, product, quantity=1, override_quantity=False):
        product_id = str(product.id)
        if product_id not in self.cart:
            self.cart[product_id] = {'quantity': 0, 'price': float(product.price)}
        if override_quantity:
            self.cart[product_id]['quantity'] = quantity
        else:
            self.cart[product_id]['quantity'] += quantity
        self.save()

    def save(self):
        self.session[settings.CART_SESSION_ID] = self.cart
        self.session['free_shipping'] = self.free_shipping
        self.session['shipping_cost'] = self.shipping_cost
        self.session['discounted_total'] = getattr(self, 'discounted_total', None)
        self.session.modified = True

    def remove(self, product):
        product_id = str(product.id)
        if product_id in self.cart:
            del self.cart[product_id]

            if len(self.cart) == 0:
                self.free_shipping = False
                self.discounted_total = None
                if 'promo_code' in self.session:
                    del self.session['promo_code']

            self.save()

    def __iter__(self):
        product_ids = self.cart.keys()
        products = Product.objects.filter(id__in=product_ids)
        cart_copy = self.cart.copy()

        items = []
        for product in products:
            item = cart_copy[str(product.id)].copy()
            item['product'] = product
            item['price'] = float(product.get_discounted_price())
            item['total_price'] = item['price'] * item['quantity']
            items.append(item)

        for item in items:
            yield item

    def __len__(self):
        return sum(item['quantity'] for item in self.cart.values())

    def get_total_price(self):
        return sum(item['total_price'] for item in self)


    def clear(self):
        self.session.pop(settings.CART_SESSION_ID, None)
        self.session.pop('free_shipping', None)
        self.session.pop('discounted_total', None)
        self.session.modified = True

    def apply_promo(self, promo):
        if promo.discount_type == 'free_shipping':
            self.free_shipping = True
            self.discounted_total = self.get_total_price()
        else:
            total = self.get_total_price()
            self.discounted_total = promo.apply_discount(total)
        self.save()

    def get_total_price_with_shipping(self):
        total = self.discounted_total if getattr(self, 'discounted_total', None) else self.get_total_price()
        if not self.free_shipping:
            total += self.shipping_cost
        return total
