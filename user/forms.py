from django import forms
from django.contrib.auth import models
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.contrib.auth.models import User
from django.forms import TextInput, EmailInput, Select, FileInput
from django.forms import widgets
from user.models import UserProfile
from order.constants import *


class SignUpForm(UserCreationForm):
    username = forms.CharField(max_length=30,label= 'User Name :')
    email = forms.EmailField(max_length=200,label= 'Email :')
    first_name = forms.CharField(max_length=100, help_text='First Name',label= 'First Name :')
    last_name = forms.CharField(max_length=100, help_text='Last Name',label= 'Last Name :')

    class Meta:
        model = User
        fields = ('username', 'email','first_name','last_name', 'password1', 'password2', )

    def __init__(self, *args, **kwargs):
        super(SignUpForm, self).__init__(*args, **kwargs)
        self.fields['username'].widget.attrs['class'] = 'form-control'
        self.fields['email'].widget.attrs['class'] = 'form-control'
        self.fields['first_name'].widget.attrs['class'] = 'form-control'
        self.fields['last_name'].widget.attrs['class'] = 'form-control'
        self.fields['password1'].widget.attrs['class'] = 'form-control'
        self.fields['password2'].widget.attrs['class'] = 'form-control'

class UserUpdateForm(UserChangeForm):
    username = forms.CharField(disabled=True, widget=TextInput(attrs={'class': 'input','placeholder':'username'}),)
    class Meta:
        model = User
        fields = ( 'username','email','first_name','last_name')
        widgets = {
            # 'username'  : TextInput(attrs={'class': 'input','placeholder':'username'}),
            'email'     : EmailInput(attrs={'class': 'input','placeholder':'email'}),
            'first_name': TextInput(attrs={'class': 'input','placeholder':'first_name'}),
            'last_name' : TextInput(attrs={'class': 'input','placeholder':'last_name' }),
        }

CITY = [
    ('Ha Noi', 'Ha Noi'),
    ('Ho Chi Minh', 'Ho Chi Minh'),
    ('Can Tho', 'Can Tho'),
]
class ProfileUpdateForm(forms.ModelForm):
    phone = forms.CharField(validators=[PHONE_NUMBER_REGEX],widget=TextInput(attrs={'class': 'input','placeholder':'phone'}))
    address = forms.CharField(required=True, widget=TextInput(attrs={'class': 'input','placeholder':'address'}),)
    class Meta:
        model = UserProfile
        fields = ('phone', 'address', 'city','country','image')
        widgets = {
            # 'phone'     : TextInput(attrs={'class': 'input','placeholder':'phone'}),
            # 'address'   : TextInput(attrs={'class': 'input','placeholder':'address'}),
            'city'      : Select(attrs={'class': 'input','placeholder':'city'},choices=CITY),
            'country'   : TextInput(attrs={'class': 'input','placeholder':'country' }),
            'image'     : FileInput(attrs={'class': 'input', 'placeholder': 'image', }),
        }