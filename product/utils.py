from django.db.models import F


def decrease_quantity_product(product, quantity=1):
    """Decrease voucher uses by quantity"""
    product.amount = F("amount") - quantity
    product.save(update_fields=["amount"])

def increase_quantity_product(product, quantity=1):
    """Increase voucher uses by quantity"""
    product.amount = F("amount") + quantity
    product.save(update_fields=["amount"])
