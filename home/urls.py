from django.urls import path
from . import views
app_name = 'home'
urlpatterns = [
    path('', views.index, name='index'),
    path('about/', views.aboutUs, name='aboutus'),
    path('contact/', views.contact, name='contact'),
    path('category/<int:id>/<slug:slug>', views.category_products, name='category_products'),
    path('search/', views.search, name='search'),
    path('search_auto/', views.search_auto, name='search_auto'),

    path('privacy/', views.privacyPolicy, name="privacyPolicy"),
    path('payment_policy/', views.payment_policy, name="payment_policy"),
    path('warranty_policy/', views.warranty_policy, name="warranty_policy"),
    path('shipping_policy/', views.shipping_policy, name="shipping_policy"),
    path('return_policy/', views.return_policy, name="return_policy"),
]   