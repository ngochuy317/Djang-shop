from order.views import shopcart
from home.models import Setting
from django.http.response import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import render
from django.http import HttpResponse
from django.contrib import messages
from django.core.paginator import Paginator
from home.models import *
from product.models import Category, Comment, Images, Product, Promotion
from order.models import OrderDetail, ShopCart
import json
import datetime
from decimal import Decimal
from django.db.models import Count, Sum
from django.conf import settings

from home.forms import SearchForm
# Create your views here.

def check_havediscount(promotions, products):
    for pr_newest in products:
        pr_newest.have_discount = False
        pr_newest.discount_price = None
        pr_newest.save()
        for promotion in promotions:
            if promotion.product.id == pr_newest.id:
                pr_newest.have_discount = True
                pr_newest.discount_price = round((pr_newest.price * (100 - promotion.discount) / 100) ,2)
                pr_newest.save()

def index(request):

    setting = Setting.objects.get(pk = 1)
    category = Category.objects.all()
    products_slider = Product.objects.all().order_by('id')[:6] #first 4 product
    product_newest = Product.objects.all().order_by('-id')[:24]#sản phẩm mới nhất
    products_lasted = Product.objects.all().order_by('create_at')[:12]
    products_picked = Product.objects.all().order_by('?')[:8] #random 4 product

    # #count số lần product title xuất hiện
    # metrics = {
    #         'frequency' : Count('product__title')
    #     }
    # products_hot = OrderDetail.objects.all().values(
    #     'product__title','price', 'product__discount_price').annotate(**metrics).order_by('-frequency') #hot products

    promotions = Promotion.objects.filter(
        start_date__lte=datetime.date.today(),
        end_date__gte=datetime.date.today()
    )

    check_havediscount(promotions, products_slider)
    check_havediscount(promotions, product_newest)
    # check_havediscount(promotions, products_lasted)

    current_user = request.user #access user session information
    # shopcart = ShopCart.objects.filter(user_id = current_user.id)
    # total = 0
    # for rs in shopcart:
    #     total += rs.product.price * rs.quantity

    page = "home"
    context = {'setting': setting, 
                'page': page, 
                'category':category,
                'products_slider':products_slider,
                'product_newest':product_newest,
                'products_lasted':products_lasted,
                'products_picked':products_picked,
                # 'products_hot': products_hot,
                # 'total':total,
                'promotions': promotions
                }
    return render(request, 'home/index.html', context)

def aboutUs(request):
    category = Category.objects.all()   #hiển thị thanh navbar
    setting = Setting.objects.get(pk=1)
    context = {'setting': setting,'category':category}
    return render(request, 'home/about.html', context)

#footer
def privacyPolicy(request):
    category = Category.objects.all()   #hiển thị thanh navbar
    setting = Setting.objects.get(pk=1)
    context = {'setting': setting,'category':category}
    return render(request, 'home/policy_privacy.html', context)

def payment_policy(request):
    category = Category.objects.all()   #hiển thị thanh navbar
    setting = Setting.objects.get(pk=1)
    context = {'setting': setting,'category':category}
    return render(request, 'home/policy_payment.html', context)

def warranty_policy(request):
    category = Category.objects.all()   #hiển thị thanh navbar
    setting = Setting.objects.get(pk=1)
    context = {'setting': setting,'category':category}
    return render(request, 'home/policy_warranty.html', context)

def shipping_policy(request):
    category = Category.objects.all()   #hiển thị thanh navbar
    setting = Setting.objects.get(pk=1)
    context = {'setting': setting,'category':category}
    return render(request, 'home/policy_shipping.html', context)

def return_policy(request):
    category = Category.objects.all()   #hiển thị thanh navbar
    setting = Setting.objects.get(pk=1)
    context = {'setting': setting,'category':category}
    return render(request, 'home/policy_return.html', context)
#end footer

def contact(request):
    category = Category.objects.all()  #hiển thị thanh navbar
    if request.method == 'POST': # check post
        form = ContactForm(request.POST)
        if form.is_valid():
            data = ContactMessage() #create relation with model
            data.name = form.cleaned_data['name'] # get form input data
            data.email = form.cleaned_data['email']
            data.subject = form.cleaned_data['subject']
            data.message = form.cleaned_data['message']
            data.ip = request.META.get('REMOTE_ADDR')
            data.save()  #save data to table
            messages.success(request,"Your message has ben sent. Thank you for your message.")
            return HttpResponseRedirect('/contact')

    setting = Setting.objects.get(pk=1)
    form = ContactForm
    context = {'setting': setting, 'form': form,'category':category}
    return render(request, 'home/contact.html', context)


def category_products(request, id, slug):
    # shopcart = ShopCart.objects.all()
    range_of_price = {
        "Under $10": 1,
        "From $10-$20": 2,
        "Above $20": 3,
        "All": 4
    }

    allgender = {
        "Men": 'men',
        "Women": 'women',
        "All": 'all'
    }

    price = request.POST.get("price", None)
    gender = request.POST.get("gender", None)

    category = Category.objects.all()
    products = Product.objects.filter(category_id=id)
    price_checked = 'All'
    gender_checked = 'All'

    #Filter product by price
    if price:
        if price == '1':
            products = products.filter(price__lte=10)
            price_checked = 'Under $10'
        elif price == '2':
            products = products.filter(price__gt=10).filter(price__lt=20)
            price_checked = 'From $10-$20'
        elif price == '3':
            products = products.filter(price__gte=20)
            price_checked = 'Above $20'
    
    if gender:
        if gender == 'men':
            products = products.filter(sex='Male')
            gender_checked = 'Men'
        elif gender == 'women':
            products = products.filter(sex='Female')
            gender_checked = 'Women'

    #Paginator
    number_of_products = 5
    paginator = Paginator(products, number_of_products)
    page_number = request.GET.get('page')
    products = paginator.get_page(page_number)

    context = {'products':products,
                'category':category,
                'range_of_price': range_of_price,
                'price_checked': price_checked,
                'allgender': allgender,
                'gender_checked': gender_checked,
                'id_category': id,
                'slug': slug,
                
                # 'shopcart':shopcart
                }
    return render(request, 'home/category_products.html', context)


def search(request):
    if request.method == 'POST': # check post
        form = SearchForm(request.POST)
        if form.is_valid():
            query = form.cleaned_data['query'] # get form input data
            catid = form.cleaned_data['catid']
            if catid==0:
                products=Product.objects.filter(title__icontains=query)  #SELECT * FROM product WHERE title LIKE '%query%'
            else:
                products = Product.objects.filter(title__icontains=query,category_id=catid)

            shopcart = ShopCart.objects.all()

            category = Category.objects.all()
            context = {'products': products, 'query':query,
                       'category': category, 'shopcart':shopcart }
            return render(request, 'home/search_products.html', context)

    return HttpResponseRedirect('/')


def search_auto(request):
  if request.is_ajax():
    q = request.GET.get('term', '')
    products = Product.objects.filter(title__icontains=q)
    results = []
    for rs in products:
      products_json = {}
      products_json = rs.title
      results.append(products_json)
    data = json.dumps(results)
  else:
    data = 'fail'
  mimetype = 'application/json'
  return HttpResponse(data, mimetype)

def product_detail(request, id, slug):
    category = Category.objects.all()
    product = Product.objects.get(pk=id)
    images = Images.objects.filter(product_id=id)
    promotions = Promotion.objects.filter(
        start_date__lte=datetime.date.today(),
        end_date__gte=datetime.date.today()
    )

    product.have_discount = False
    product.discount_price = None
    product.save()
    for promotion in promotions:
        if promotion.product.id == product.id:
            product.have_discount = True
            product.discount_price = round((product.price * (100 - promotion.discount) / 100), 2)
            product.save()
    
    comments = Comment.objects.filter(product_id=id,status='True')

    #Paginator review
    number_of_comments = 5
    paginator = Paginator(comments, number_of_comments)
    page_number = request.GET.get('page')
    comments = paginator.get_page(page_number)

    context = {'product':product,
                'category':category,
                'images': images,
                'comments':comments,
                'promotions': promotions
                }
    return render(request, 'home/product_detail.html', context)
