"""mysite URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from product.models import Category
from django.contrib import admin
from django.urls import path
from django.urls.conf import include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic.base import TemplateView
from home import views
import home
from order import views as OrderViews
from user import views as UserViews
from django.contrib.auth import views as auth_views
urlpatterns = [
    path('admin/', admin.site.urls),

    #home
    path('', include('home.urls')),
    path('home/', include('home.urls')),

    #product
    path('product/', include('product.urls')),
    path('product/<int:id>/<slug:slug>/', views.product_detail, name='product_detail'),

    #orders
    path('order/', include('order.urls')),

    #shop cart in home
    path('shopcart/', OrderViews.shopcart, name='shopcart'),

    #for user
    path('user/', include('user.urls')),
    path('login/', UserViews.login_form, name='login_form'),
    path('logout/', UserViews.logout_func, name='logout_func'),
    path('signup/', UserViews.signup_form, name='signup_form'),

    #for admin in product detail
    path('ckeditor/', include('ckeditor_uploader.urls')),   

    #for reset password
    path('reset_password/', 
    auth_views.PasswordResetView.as_view(template_name="user/password_reset.html",
                                        extra_context={'category': Category.objects.all()}), 
                                        name="reset_password"), #submit email form

    path('reset_password_sent/', 
    auth_views.PasswordResetDoneView.as_view(template_name="user/password_reset_sent.html", 
                                            extra_context={'category': Category.objects.all()}),
                                            name="password_reset_done"), #email sent success message

    path('reset/<uidb64>/<token>', 
    auth_views.PasswordResetConfirmView.as_view(template_name="user/password_reset_form.html",
                                                extra_context={'category': Category.objects.all()}), 
                                                name="password_reset_confirm"), #link to password Reset from in email

    path('reset_password_complete/', 
    auth_views.PasswordResetCompleteView.as_view(template_name="user/password_reset_done.html",
                                                extra_context={'category': Category.objects.all()}),
                                                name="password_reset_complete"), #password successfully changed message

]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)