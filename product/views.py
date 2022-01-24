from django.http.response import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.http import HttpResponse
from product.models import *
from django.contrib import messages
# Create your views here.
def index(request):
    return HttpResponse('this is product')

def addComment(request, id):
    url = request.META.get('HTTP_REFERER') #get last url
    # return HttpResponse(url)
    if request.method == 'POST': # check post
        form = CommentForm(request.POST)
        if form.is_valid():
            data = Comment()  #create relation with model
            # get form input data
            data.subject = form.cleaned_data['subject']
            data.comment = form.cleaned_data['comment']
            data.rate = form.cleaned_data['rate']
            data.ip = request.META.get('REMOTE_ADDR')
            data.product_id = id
            current_user = request.user
            data.user_id = current_user.id
            data.save()
            messages.success(request,"Your review has been sent. Thank you for your comment.")
            return HttpResponseRedirect(url)

    return HttpResponseRedirect(url)