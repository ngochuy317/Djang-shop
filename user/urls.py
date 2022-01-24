from django.urls import path
from . import views
from django.contrib.auth import views as auth_views
urlpatterns = [
    path('', views.index, name='index'),
    path('update/', views.user_update, name='user_update'),
    path('password/', views.user_password, name='user_password'),
    path('orders/', views.user_orders, name='user_orders'),
    path('orders_product/', views.user_orderProduct, name='user_orderProduct'),
    path('order_detail/<int:id>', views.user_order_detail, name='user_order_detail'),
    path('order_product_detail/<int:id>/<int:order_id>', views.user_order_product_detail, name='user_order_product_detail'),
    path('export_invoice/<int:id>', views.export_invoice, name='export_invoice'),
    path('comments/', views.user_comments, name='user_comments'),
    path('deletecomment/<int:id>', views.user_delete_comment, name='user_delete_comment'), 

]   