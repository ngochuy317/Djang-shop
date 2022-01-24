from django.contrib import admin
from django.db.models import Count, Sum
from . models import SalesReport, ProductReport

from product.models import Product
from order.models import OrderDetail

from rangefilter.filters import DateRangeFilter

# Register your models here.

@admin.register(SalesReport)
class SalesReportAdmin(admin.ModelAdmin):
    change_list_template = 'admin/sale_summary_change_list.html'
    list_filter = ['status', 'user', ('create_at', DateRangeFilter),]

    def get_rangefilter_create_at_title(self, request, field_path):
        return 'By date'

    def has_add_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def changelist_view(self, request, extra_context=None):
        response = super().changelist_view(
            request,
            extra_context=extra_context,
        )

        try:
            qs = response.context_data['cl'].queryset
        except (AttributeError, KeyError):
            return response

        metrics = {
            'total': Sum('total'),
            'total_after_used_voucher': Sum('total_after_used_voucher'),
        }

        response.context_data['summary'] = list(
            qs
            .values('first_name', 'status', 'create_at')
            .annotate(**metrics)
        )

        response.context_data['summary_total'] = dict(
            qs.aggregate(**metrics)
        )

        return response


@admin.register(ProductReport)
class ProductReportAdmin(admin.ModelAdmin):
    change_list_template = 'admin/product_summary_change_list.html'
    list_filter = ['user',('create_at', DateRangeFilter)]

    def has_add_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def changelist_view(self, request, extra_context=None):
        response = super().changelist_view(
            request,
            extra_context=extra_context,
        )

        try:
            qs = response.context_data['cl'].queryset
        except (AttributeError, KeyError):
            return response

        metrics = {
            'frequency' : Count('product__title')
        }

        response.context_data['quantity'] = list(
            qs
            .values('product__title', 'price', 'product__discount_price')
            .annotate(**metrics)
            .order_by('-frequency')
        )

        return response