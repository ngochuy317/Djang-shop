from django.conf import settings
from django.forms.formsets import DELETION_FIELD_NAME
import user
from user.forms import SignUpForm
from django.http.response import HttpResponseRedirect
from django.shortcuts import redirect, render
from django.http import HttpResponse
from product.models import *
from user.models import *
from order.models import *
from order.cart import persist_session_vars

from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.template.loader import get_template
from user.forms import SignUpForm, UserUpdateForm, ProfileUpdateForm
from django.contrib.auth.forms import PasswordChangeForm

from django.core.paginator import Paginator
from xhtml2pdf import pisa
# Create your views here.


@login_required(login_url='/login') # Check login
def index(request):
    category = Category.objects.all()
    current_user = request.user  # Access User Session information
    profile = UserProfile.objects.get(user_id=current_user.id)
    context = {'category': category,
               'profile':profile}
    return render(request,'user/user_profile.html',context)

def login_form(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            current_user = request.user 
            userprofile = UserProfile.objects.get(user_id = current_user.id)
            request.session['userimage'] = userprofile.image.url
            #redirect to success page
            return HttpResponseRedirect('/home')
        else:
            messages.warning(request, "login error!! User or Password is incorrect")
            return HttpResponseRedirect('/login')
    category = Category.objects.all()
    context = {'category': category}
    return render(request, 'user/login_form.html', context)

def signup_form(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            form.save() #complete sign in
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=password)
            login(request, user)

            #create data in profile table for user
            current_user = request.user
            data = UserProfile()
            data.user_id = current_user.id
            data.image = "images/users/user.png"
            data.save()
            messages.success(request, "Your account has been created!")
            return HttpResponseRedirect('/')
        else:
            messages.warning(request, form.errors)
            return HttpResponseRedirect('/signup')

    form = SignUpForm()
    category = Category.objects.all()
    context = {'category': category,
                'form': form}
    return render(request, 'user/signup_form.html', context)


@persist_session_vars([settings.CART_SESSION_ID, settings.VOUCHER_SESSION_ID])
def logout_func(request):
    logout(request)
    return HttpResponseRedirect('/')

def user_update(request):
    if request.method == 'POST':
        user_form = UserUpdateForm(request.POST, instance=request.user) # request.user is user  data
        profile_form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user.userprofile)
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, 'Your account has been updated!')
            return HttpResponseRedirect('/user')
        else:
            messages.warning(request, profile_form.errors )
            return HttpResponseRedirect('/user/update')
    else:
        category = Category.objects.all()
        user_form = UserUpdateForm(instance=request.user)
        profile_form = ProfileUpdateForm(instance=request.user.userprofile) #"userprofile" model -> OneToOneField relation with user
        context = {
            'category': category,
            'user_form': user_form,
            'profile_form': profile_form,
        }
        return render(request, 'user/user_update.html', context)

def user_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # Important!
            messages.success(request, 'Your password was successfully updated!')
            return HttpResponseRedirect('/user')
        else:
            messages.error(request, 'Please correct the error below.<br>'+ str(form.errors))
            return HttpResponseRedirect('/user/password')
    else:
        category = Category.objects.all()
        form = PasswordChangeForm(request.user)
        context =  {'form': form,
                    'category':category}
        return render(request, 'user/user_password.html', context)

#My Order page
def user_orders(request):
    category = Category.objects.all()
    current_user = request.user
    orders = Order.objects.filter(user_id = current_user.id).order_by("-create_at")

    #Paginator order products
    number_of_order = 10
    paginator = Paginator(orders, number_of_order)
    page_number = request.GET.get('page')
    orders = paginator.get_page(page_number)
    
    context = {'category': category,
                'orders': orders}
    return render(request, 'user/user_orders.html', context)

#Order detail & produt detail page
def user_order_detail(request, id):
    category = Category.objects.all()
    current_user = request.user
    order = Order.objects.get(user_id = current_user.id, id=id)
    orderDetails = OrderDetail.objects.filter(order_id=id)
    context =  {
        'category': category,
        'order': order,
        'orderDetails': orderDetails
    }
    return render(request, "user/user_order_detail.html", context)


#User Order Product page
def user_orderProduct(request):
    category = Category.objects.all()
    current_user = request.user
    order_product = OrderDetail.objects.filter(user_id = current_user.id)

    #Paginator order products
    number_of_order_product = 10
    paginator = Paginator(order_product, number_of_order_product)
    page_number = request.GET.get('page')
    order_product = paginator.get_page(page_number)

    context = {'category': category,
                'order_product': order_product}
    return render(request, 'user/user_order_product.html', context)


def user_order_product_detail(request, id, order_id):
    category = Category.objects.all()
    current_user = request.user
    order = Order.objects.get(user_id = current_user.id, id=order_id)
    orderDetails = OrderDetail.objects.filter(id=id, user_id = current_user.id)
    context =  {
        'category': category,
        'order': order,
        'orderDetails': orderDetails
    }
    return render(request, "user/user_order_detail.html", context)


def export_invoice(request, id):
    shipping_fee = None
    category = Category.objects.all()
    current_user = request.user
    order = Order.objects.get(id=id)
    orderDetails = OrderDetail.objects.filter(order_id=id)
    # Set template to export
    template_path = 'user/invoice.html'
    template = get_template(template_path)
    
    context =  {
        'category': category,
        'order': order,
        'orderDetails': orderDetails,
        'shipping_fee' : shipping_fee,
        'current_user': current_user
    }
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="invoice.pdf"'
    html = template.render(context)
    pisa_status = pisa.CreatePDF(html, dest=response, link_callback=request.path)
    
    if pisa_status.err:
        return HttpResponse('We had some errors <pre>'+ html + '</pre>')
    
    return response

def user_comments(request):
    category = Category.objects.all()
    current_user = request.user
    comments = Comment.objects.filter(user_id=current_user.id)
    context = {
        'category':category,
        'comments':comments,
    }
    return render(request, "user/user_comments.html", context)

def user_delete_comment(request, id):
    current_user = request.user
    Comment.objects.filter(id=id, user_id=current_user.id).delete()
    messages.success(request, 'Comment deleted..')
    return HttpResponseRedirect('/user/comments')

