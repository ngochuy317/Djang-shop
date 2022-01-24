from product.models import Category
from django.contrib import admin
from product.models import *
from mptt.admin import DraggableMPTTAdmin
# Register your models here.

class CategoryAdmin(admin.ModelAdmin):
    list_display = ['title','parent', 'status']
    list_filter = ['status']


class CategoryAdmin2(DraggableMPTTAdmin):
    mptt_indent_field = "title"
    list_display = ('tree_actions', 'indented_title',
                    'related_products_count', 'related_products_cumulative_count')
    list_display_links = ('indented_title',)
    prepopulated_fields = {'slug': ('title',)}

    # inlines = [CategoryLangInline]
    def get_queryset(self, request):
        qs = super().get_queryset(request)

        # Add cumulative product count
        qs = Category.objects.add_related_count(
                qs,
                Product,
                'category',
                'products_cumulative_count',
                cumulative=True)

        # Add non cumulative product count
        qs = Category.objects.add_related_count(qs,
                 Product,
                 'category',
                 'products_count',
                 cumulative=False)
        return qs

    def related_products_count(self, instance):
        return instance.products_count
    related_products_count.short_description = 'Related products (for this specific category)'

    def related_products_cumulative_count(self, instance):
        return instance.products_cumulative_count
    related_products_cumulative_count.short_description = 'Related products (in tree)'


# add thêm 3 fields image vào Product trong Admin
class ProductImageInline(admin.TabularInline):
    model = Images
    extra = 3

class ProductAdmin(admin.ModelAdmin):
    list_display = ['title','category', 'price','image_tag', 'amount']
    list_filter = ['category','sex']
    readonly_fields = ('image_tag',)
    inlines = [ProductImageInline]
    prepopulated_fields = {'slug': ('title',)}
    exclude = ['have_discount', 'discount_price']


class CommentAdmin(admin.ModelAdmin):
    list_display = [ 'product', 'user' ,'subject','comment', 'rate','status','create_at']
    list_filter = ['status','rate']
    readonly_fields = ('product', 'user' ,'subject','comment', 'rate', 'ip')





admin.site.register(Category, CategoryAdmin2)   
admin.site.register(Product, ProductAdmin) 
admin.site.register(Images) 
admin.site.register(Comment, CommentAdmin)
admin.site.register(Promotion)
admin.site.register(Voucher)
