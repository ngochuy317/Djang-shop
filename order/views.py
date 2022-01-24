from django.http.request import HttpRequest
from product.models import Category, Product
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from order.models import OrderDetail, ShopCart, ShopCartForm, OrderForm, Order
from django.http.response import  HttpResponseRedirect, JsonResponse
from django.shortcuts import get_object_or_404, render
from django.http import HttpResponse

from django.utils.crypto import get_random_string

from user.models import *
from product.models import Promotion, Voucher
from product.utils import decrease_quantity_product

from .cart import Cart

import datetime


# Create your views here.
def index(request):
    return HttpResponse('order page')

# @login_required(login_url='/login') # Check login
# def addToShopCart(request,id):
#     url =  request.META.get('HTTP_REFERER') #get last url
#     current_user = request.user #access user session information

#     checkproduct = ShopCart.objects.filter(product_id = id) #ccheck product in shopcart
#     if checkproduct:
#         control = 1 #the product is in cart
#     else:
#         control = 0 #the product is not in cart

#     if request.method == 'POST': #if there is a POST  (for product detail)
#         form = ShopCartForm(request.POST)
#         if form.is_valid():
#             if control == 1:
#                 data = ShopCart.objects.get(product_id=id)
#                 data.quantity += form.cleaned_data['quantity']
#                 data.save() #save data
#             else: #insert to shopcart
#                 data = ShopCart()
#                 data.user_id = current_user.id
#                 data.product_id = id
#                 data.quantity = form.cleaned_data['quantity']
#                 data.save()
#         messages.success(request, "Product added to Cart")
#         return HttpResponseRedirect(url)

#     else: #if no POST ( just add one product)
#         if control ==1 : #update shopcart
#             data = ShopCart.objects.get(product_id = id)
#             data.quantity += 1
#             data.save()
#         else: #insert to shopcart
#             data = ShopCart()
#             data.user_id = current_user.id
#             data.product_id = id
#             data.quantity = 1
#             data.save()
#         messages.success(request, "Product added to Cart")
#         return HttpResponseRedirect(url)


def addToShopCart(request, id):
    """
    Method add product to session cart
    Param: 
        product_id : int
        quantity : int
    Result:
        Save product to cart session, 
    Return total quantity 
    
    """
    cart = Cart(request)
    if request.POST.get('action') == 'post':
        id = int(request.POST.get('id'))
        quantity = int(request.POST.get('qty'))
        product = get_object_or_404(Product, id=id)
        cart.add(product=product, quantity=quantity)
        cart_qty_total = cart.__len__()
        cart_subtotal = cart.get_subtotal_price()
        context = {
            'subtotal': str(cart_subtotal),
            'quantity': cart_qty_total
        }
        
        response = JsonResponse(context)
    return response


# def shopcart(request):
#     category = Category.objects.all()
#     current_user = request.user #access user session information
#     shopcart = ShopCart.objects.filter(user_id = current_user.id)

#     total = 0
#     for rs in shopcart:
#         total += rs.product.price * rs.quantity
#     # return HttpResponse(str(total))
    
#     context = {'shopcart': shopcart,
#                 'category':category,
#                 'total':total}
#     return render(request, 'order/shopcart_products.html', context)


def shopcart(request):
    """
    Show all products user added to session cart
    """
    category = Category.objects.all()
    cart = Cart(request)
    context = {
        'cart': cart,
        'category': category
    }
    return render(request,'order/shopcart_products.html', context)


# @login_required(login_url='/login') # Check login
# def deletefromcart(request, id):
#     ShopCart.objects.filter(id=id).delete()
#     messages.success(request, "Your item deleted from Shop Cart")
#     return HttpResponseRedirect("/shopcart")


def deletefromcart(request):
    """
    Method update product from session cart
    Param: 
        product_id : int
        quantity : int
    Result:
        update quantity of selected product from cart session 
    Return: total quantiy, total price of cart
    
    """
    cart = Cart(request)
    response = None
    if request.POST.get('action') == "post":
        id = int(request.POST.get('id'))
        cart.delete(product_id=id)
        cart_qty_total = cart.__len__()
        cart_subtotal = cart.get_subtotal_price()
        cart_totalprice = cart.get_total_price()
        context = {
            'quantity': cart_qty_total,
            'subtotal': str(cart_subtotal),
            'total': cart_totalprice
        }
        response = JsonResponse(context)
    return response


@login_required(login_url='login_form')
def orderdetail(request):
    category = Category.objects.all()
    current_user = request.user
    # shopcart = ShopCart.objects.filter(user_id=current_user.id)
    session = request.session
    cart = Cart(request)
    # total = 0
    # for rs in shopcart:
    #     total += rs.product.price * rs.quantity

    # take voucher from session
    if cart.voucher:
        code = cart.voucher['voucher']['code']
        discount = cart.voucher['voucher']['discount']
        cart_totalprice = cart.add_coupon(code, discount)
    else:
        discount = None
        cart_totalprice = None
    

    if request.method == 'POST':  # if there is a post
        form = OrderForm(request.POST)
        #return HttpResponse(request.POST.items())
        if form.is_valid():
            # Send Credit card to bank,  If the bank responds ok, continue, if not, show the error
            # ..............

            data = Order()
            data.first_name = form.cleaned_data['first_name'] #get product quantity from form
            data.last_name = form.cleaned_data['last_name']
            data.address = form.cleaned_data['address']
            data.city = form.cleaned_data['city']
            data.phone = form.cleaned_data['phone']
            data.user_id = current_user.id
            data.total = cart.get_total_price()
            data.voucher = cart.get_voucher_code()
            data.total_after_used_voucher = cart.get_total_price_after_user_voucher()

            # if 'voucher' not in request.session:
            #     data.voucher = None
            #     data.total_after_used_voucher = None
            # else:
            #     discount = cart.voucher['voucher']['discount']
            #     code = cart.voucher['voucher']['code']
            #     voucher = Voucher.objects.get(code = code)
            #     data.voucher = voucher
            #     data.total_after_used_voucher = cart.add_coupon(code, discount)
                
            data.ip = request.META.get('REMOTE_ADDR')
            ordercode= get_random_string(5).upper() # random cod
            data.code =  ordercode
            data.save() #

            #move shopcart items to order detail item
            # shopcart = ShopCart.objects.filter(user_id=current_user.id)
            for rs in cart:
                detail = OrderDetail()
                detail.order_id     = data.id # Order Id
                detail.product_id   = rs['product_id']
                detail.user_id      = current_user.id
                detail.quantity     = rs['quantity']
                detail.price        = rs['price']
                detail.amount       = rs['total_price']
                detail.save()
                # ***Reduce quantity of sold product from Amount of Product
                product = Product.objects.get(id=rs['product_id'])
                decrease_quantity_product(product, rs['quantity'])
                #-----------------------

            # ShopCart.objects.filter(user_id=current_user.id).delete() # Clear & Delete shopcart
            # request.session['cart_items']=0
            cart.clear()
            try:
                cart.clear_voucher()
            except:
                pass
            # messages.success(request, "Your Order has been completed. Thank you ")
            return render(request, 'order/order_completed.html',{'ordercode':ordercode,'category': category})
        else:
            messages.warning(request, form.errors)
            return HttpResponseRedirect("/order/orderdetail")
    # voucher = Voucher.objects.get(code = code)
    form= OrderForm()
    profile = UserProfile.objects.get(user_id=current_user.id)
    context = {'shopcart': cart,
               'category': category,
            #    'total': total,
               'form': form,
               'profile': profile,
               'discount': discount,
               'cart_totalprice': cart_totalprice,
            #    'voucher':voucher,
               }
    return render(request, 'order/order_form.html', context)


def add_coupon(request):
    """
    Method add voucher to session and get value from voucher add to cart session 
    Param: 
        code : from request.POST
    result:
        add voucher to session
    Return: json to ajax method
    """
    cart = Cart(request)
    session = request.session
    if request.method=="POST":
        code = request.POST.get('code')
        # try:    
        voucher = Voucher.objects.get(code = code)
        if voucher.start_date <= datetime.date.today() <= voucher.end_date:
            cart_totalprice = cart.add_coupon(voucher.code, voucher.discount)
            # if 'voucher' not in session:
            #     session['voucher'] = {
            #         'code': code,
            #         'discount': voucher.discount,
            #     }

            # else:
            #     session['voucher']['discount'] = voucher.discount
            #     session['voucher']['code'] = voucher.code
            #     session.modified = True
            context = {
                'coupon_price': voucher.discount,
                'cart_totalprice': str(cart_totalprice)
            }
            response = JsonResponse(context)
            return response
        # else:
        #     response = JsonResponse({"error": "Coupon can not use in this time"})
        #     response.status_code = 403
        #     return response
        # except:
        #     response = JsonResponse({"error": "Coupon invalid"})
        #     response.status_code = 403
        #     return response

def remove_coupon(request):
    cart = Cart(request)
    try:
        cart.clear_voucher()
    except:
        pass
    get_voucher_value = cart.get_voucher_value()
    get_total_price_after_user_voucher = cart.get_total_price_after_user_voucher()
    context = {
        'get_voucher_value' : str(get_voucher_value),
        'get_total_price_after_user_voucher': get_total_price_after_user_voucher
    }
    response = JsonResponse(context)
    return response
    