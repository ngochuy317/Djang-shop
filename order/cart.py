from decimal import Decimal
from django.conf import settings
from functools import wraps

from product.models import Product, Voucher


class Cart(object):
    """
    A base Cart class, providing some default behaviors that can be
    inherited or overrided, as necessary    
    """
    def __init__(self, request):
        self.session = request.session
        cart = self.session.get(settings.CART_SESSION_ID)
        voucher = self.session.get(settings.VOUCHER_SESSION_ID)

        if settings.CART_SESSION_ID not in request.session:
            cart = self.session[settings.CART_SESSION_ID] = {}

        if settings.VOUCHER_SESSION_ID not in request.session:
            voucher = self.session[settings.VOUCHER_SESSION_ID] = {}

        self.cart = cart
        self.voucher = voucher

    def add(self, product, quantity):
        """
        Add and update the user's cart session data
        """
        id = str(product.id) 
        if id in self.cart:
            self.cart[id]["quantity"] = quantity

        else:
            if product.have_discount:
                self.cart[id] = {
                    "price": str(product.discount_price),
                    "quantity": quantity
                }
            else:
                self.cart[id] = {
                    "price": str(product.price),
                    "quantity": quantity
                }
  
        self.save()

    def __iter__(self):
        """
        Collect the product id in cart session data to make a query set
        return products 
        """
        list_ids = self.cart.keys()
        products = Product.objects.filter(id__in=list_ids)
        cart = self.cart.copy()

        for product in products:
            cart[str(product.id)]['product'] = product.title
            cart[str(product.id)]['product_id'] = product.id
            cart[str(product.id)]['product_image'] = product.image.url
            cart[str(product.id)]['product_slug'] = product.slug
            cart[str(product.id)]['product_price'] = product.price
            cart[str(product.id)]['product_havediscount'] = product.have_discount
            cart[str(product.id)]['product_discount_price'] = product.discount_price
            cart[str(product.id)]['product_quantity_available'] = product.amount
            

        for item in cart.values():
            item['price'] = float(item['price'])
            item['total_price'] = float(item['price'] * item['quantity'])
            yield item

    def __len__(self):
        """
        Get the cart data and count the quantity of all products
        """
        return sum(item["quantity"] for item in self.cart.values())

    def add_coupon_to_session(self, code, discount):
        """
        add coupon to session
        """
        if not self.voucher:
            self.voucher["voucher"] = {
                    "code": code,
                    "discount": discount
            }
            self.save()
        if 'voucher' in self.voucher:
            self.voucher["voucher"]["code"] = code
            self.voucher["voucher"]["discount"] = discount
            self.save()

    def add_coupon(self, code=None, discount=0):
        """
        minus value of coupon when user add coupon, value = 0 if no coupon
        """
        subtotal = self.get_subtotal_price()
        
        self.add_coupon_to_session(code, discount)

        total = round((subtotal * 0.01*(100 - discount)),2)

        self.voucher["voucher"]["total_after_used_voucher"] = total

        self.save()

        return total

    def get_voucher_value(self):
        if self.voucher:
            return f"-{self.voucher['voucher']['discount']}%"
        else:
            return None

    def get_voucher_code(self):
        if self.voucher:
            code = self.voucher['voucher']['code']
            voucher = Voucher.objects.get(code = code)
            return voucher
        else:
            return None

    def get_total_price_after_user_voucher(self):
        if self.voucher:
            if self.cart:
                return self.voucher['voucher']['total_after_used_voucher']
            else:
                return 0
        else:
            return self.get_total_price()
    
    def get_subtotal_price(self):
        """
        return subtotal of items in cart
        """
        if self.cart:
            return round(sum(float(item['price']) * item['quantity']
                for item in self.cart.values()),2)
        else:
            return 0
    
    def get_total_price(self):
        """
        get total price of total items in cart, include shipping and coupon value
        """
        subtotal = self.get_subtotal_price()
        total = subtotal
        return total
    
    def delete(self, product_id):
        """
        Delete product id from cart session data
        """
        id = str(product_id)
        if id in self.cart:
            del self.cart[id]
            self.save()
    
    def update(self, product_id, quantity):
        """
        Update values in cart session data
        """
        id = str(product_id)
        if id in self.cart:
            self.cart[id]["quantity"] = quantity
        self.save()
    
    def clear(self):
        """
        Remove cart from session
        """
        del self.session[settings.CART_SESSION_ID]

        self.save()

    def clear_voucher(self):
        """
        Remove voucher from session
        """
        del self.voucher["voucher"]
        del self.session[settings.VOUCHER_SESSION_ID]

        self.save()

    def save(self):
        """
        Save data in session when add, update, delete
        """
        self.session.modified = True

class persist_session_vars(object):
    """
    Save session when user log out
    """
    def __init__(self, vars):
        self.vars = vars

    def __call__(self, view_func):

        @wraps(view_func)
        def inner(request, *args, **kwargs):
            # Backup first
            session_backup = {}
            for var in self.vars:
                try:
                    session_backup[var] = request.session[var]
                except KeyError:
                    pass

            # Call the original view
            response = view_func(request, *args, **kwargs)

            # Restore variables in the new session
            for var, value in session_backup.items():
                request.session[var] = value

            return response

        return inner
    
