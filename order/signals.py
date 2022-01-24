
from django.db.models.signals import post_save
from django.contrib.auth.models import User
from django.dispatch import receiver
from .models import Order, OrderDetail
from .admin import OrderAdmin

from product.utils import increase_quantity_product


@receiver(post_save, sender=Order)
def post_save_update_status_order(sender, instance, **kwargs):
    if instance.status == 'Canceled':
        print("Canceled")
        id = instance.id
        orderdetails = OrderDetail.objects.filter(order__id=id)
        for orderdetail in orderdetails:
            product = orderdetail.product
            quantity = orderdetail.quantity
            increase_quantity_product(product=product, quantity=quantity)
