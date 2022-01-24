from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name="index"),
    path('addtoshopcart/<int:id>',views.addToShopCart, name="addtoshopcart"),
    # path('shopcart/', views.shopcart, name="shopcart"),
    path('deletefromcart/',views.deletefromcart, name="deletefromcart"),
    path('orderdetail/',views.orderdetail, name="orderdetail"),
    path('addcoupon/', views.add_coupon, name='addcoupon'),
    path('removecoupon/', views.remove_coupon, name='removecoupon'),
]