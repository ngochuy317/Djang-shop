from django.db import models

# Create your models here.

class YourCategory(models.Model):
    category_name = models.CharField(max_length=100)
    def __unicode__(self):
         return self.category_name

class YourModel(models.Model):
    name = models.CharField(max_length=100)
    included_categories = models.ManyToManyField(YourCategory)
    def __unicode__(self):
         return self.name
