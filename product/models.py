from django.db import models

from django.utils.safestring import mark_safe
from ckeditor_uploader.fields import RichTextUploadingField
from mptt.fields import TreeForeignKey
from mptt.models import MPTTModel
from django.urls import reverse
from django.forms import ModelForm, TextInput, Textarea, widgets
from django.contrib.auth.models import User
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db.models import Avg, Count
# Create your models here.
class Category(MPTTModel):
    STATUS = (
        ('True', 'True'),
        ('False', 'False'),    
    )
    parent = TreeForeignKey('self', blank=True, null=True, related_name='children', on_delete=models.CASCADE)
    title = models.CharField(max_length=30)
    keywords = models.CharField(max_length=255)
    description = models.CharField(max_length=255)
    # image = models.ImageField(blank=True, upload_to = 'images/')
    status = models.CharField(max_length=10, choices=STATUS)
    slug = models.SlugField(null=False, unique=True)
    create_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)

    def  __str__(self):
        return self.title
    
    class MPTTMeta:
        order_insertion_by = ['title']
    
    def get_absolute_url(self):
        return reverse('category_detail', kwargs={'slug': self.slug})
    

    #dùng để biết category tree trong trang Product-Admin
    def __str__(self):                           # __str__ method elaborated later in
        full_path = [self.title]                  # post.  use __unicode__ in place of
        k = self.parent
        while k is not None:
            full_path.append(k.title)
            k = k.parent
        return ' / '.join(full_path[::-1])
    
    class Meta:
        verbose_name_plural = "Categories"

class Product(models.Model):
    STATUS = (
        ('True', 'True'),
        ('False', 'False'),    
    )
    category = models.ForeignKey(Category, on_delete=models.CASCADE) #many to one relation with Category
    title = models.CharField(max_length=100)
    keywords = models.CharField(max_length=255)
    description = models.CharField(max_length=255)
    image = models.ImageField(blank=True, upload_to = 'images/', null= False)
    price = models.FloatField()
    amount = models.IntegerField(verbose_name='Inventory')
    # min_amount = models.IntegerField()
    detail = RichTextUploadingField()
    slug = models.SlugField(null=False, unique=True)
    status = models.CharField(max_length=10, choices=STATUS)
    create_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)
    have_discount = models.BooleanField(default=False)
    discount_price = models.FloatField(blank=True, null=True)
    SEX = (
        ('Male', 'Male'),
        ('Female', 'Female'),
    )
    sex = models.CharField(max_length=10, choices=SEX, blank=True, null=True)

    def __str__(self):
        return self.title

    # Image tag ảnh trong admin
    def image_tag(self):
        if self.image.url is not None:
            return mark_safe('<img src="{}" height="50"/>'.format(self.image.url))
        else:
            return ""

    def get_absolute_url(self):
        return reverse('category_detail', kwargs={'slug': self.slug})
        ## method to create a fake table field in read only mode
    # def image_tag(self):
    #         return mark_safe('<img src="{}" height="50"/>'.format(self.image.url))
        
    # image_tag.short_description = 'Image'

    #  ảnh phụ của product

        # count averate star
    def average_star(self):
        stars = Comment.objects.filter(product=self, status=True).aggregate(average=Avg('rate'))
        avg = 0
        if stars["average"] is not None:
            avg = float(stars["average"])
        return avg

    #count review
    def count_review(self):
        reviews = Comment.objects.filter(product=self, status=True).aggregate(count=Count('id'))
        num = 0
        if reviews["count"] is not None:
            num = int(reviews["count"])
        return num


class Images(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    title = models.CharField(max_length=50, blank=True)
    image = models.ImageField(blank=True, upload_to = 'images/')

    def __str__(self):
        return self.title

    #change name in admin
    class Meta:
        verbose_name_plural = "Images"

class Comment(models.Model):
    STATUS = (  
        ('True', 'True'),
        ('False', 'False'),    
    )
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    subject = models.CharField(max_length=50, blank=True)
    comment = models.CharField(max_length=250, blank=True)
    rate = models.IntegerField(default=1)
    ip = models.CharField(max_length=20, blank=True)
    status = models.CharField(max_length=10, choices=STATUS, default='True')
    create_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.subject

class CommentForm(ModelForm):
    class Meta:
        model = Comment
        fields = ['subject', 'comment', 'rate']


class Promotion(models.Model):
    discount = models.IntegerField(
        validators=[
            MaxValueValidator(100),
            MinValueValidator(1)
        ])
    start_date = models.DateField()
    end_date = models.DateField()
    product = models.ForeignKey(Product, on_delete=models.CASCADE)

    def __str__(self) -> str:
        return f'discount {self.discount}% on {self.product.title} from {self.start_date} to {self.end_date}'


class Voucher(models.Model):
    code = models.CharField(unique=True, max_length = 20)
    discount = models.IntegerField(
        validators=[
            MaxValueValidator(100),
            MinValueValidator(10)
        ])
    start_date = models.DateField()
    end_date = models.DateField()

    def __str__(self) -> str:
        return f'code {self.code} to discount {self.discount}%'
