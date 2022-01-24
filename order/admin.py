from django.contrib import admin
from django.contrib.admin import DateFieldListFilter
from django.utils.html import format_html
from product.models import Voucher
# Register your models here.
from order.models import *


# class ShopCartAdmin(admin.ModelAdmin):
#     list_display = ['product', 'user', 'quantity', 'price', 'amount']
#     list_filter = ['user']

class OrderDetailline(admin.TabularInline):
    model = OrderDetail
    readonly_fields = ('user', 'product','price','quantity','amount')
    can_delete = False
    extra = 0
    exclude = ['status']


class OrderAdmin(admin.ModelAdmin):
    list_display = ['id','first_name', 'last_name','phone','city','total','status', "export_invoice"]
    list_filter = ['status',]
    readonly_fields = ('user','address','city','country','phone','first_name','ip', 'last_name','phone','city','total','voucher', 'total_after_used_voucher','create_at')
    can_delete = False
    inlines = [OrderDetailline]

    def export_invoice(self, obj):
        return format_html(
            '<a class="btn btn-info" href="/user/export_invoice/{}"> Export </a>', 
          obj.id
        )


class OrderDetailAdmin(admin.ModelAdmin):
    list_display = ['order_id','user', 'product','price','quantity','amount']
    list_filter = ['user']

    

    
# admin.site.register(ShopCart, ShopCartAdmin)
admin.site.register(Order, OrderAdmin)
admin.site.register(OrderDetail, OrderDetailAdmin)
