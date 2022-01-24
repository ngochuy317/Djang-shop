from django.contrib import admin
from django import forms
from .models import YourCategory, YourModel
from django.contrib.admin.widgets import FilteredSelectMultiple  

# Register your models here.
class YourModelForm(forms.ModelForm):
    included_categories = forms.ModelMultipleChoiceField(widget=FilteredSelectMultiple('included_categories', False),
            queryset = YourCategory.objects.all())#here you can filter for what choices you need

class YourModelAdmin(admin.ModelAdmin):
    form = YourModelForm


admin.site.register(YourModel, YourModelAdmin)
admin.site.register(YourCategory)