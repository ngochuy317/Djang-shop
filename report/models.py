from django.db import models
from order.models import Order, OrderDetail

# Create your models here.

class SalesReport(Order):
    class Meta:
        proxy = True


class ProductReport(OrderDetail):
    class Meta:
        proxy = True
