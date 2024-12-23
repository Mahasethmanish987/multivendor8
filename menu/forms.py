from .models import Category,FoodItem
from django import forms 

class FoodItemForm(forms.ModelForm):
   class Meta:
      model=FoodItem
      fields=['food_title','description','category','price','image','is_available']

class CategoryForm(forms.ModelForm):
   class Meta:
      model=Category
      fields=['category_name','description']