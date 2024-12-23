from django.contrib import admin
from .models import FoodItem,Category

# Register your models here.
class CategoryAdmin(admin.ModelAdmin):
    list_display=('category_name','created_at')
class FoodItemAdmin(admin.ModelAdmin):
    list_display=('food_title','price','created_at')
admin.site.register(Category,CategoryAdmin)    
admin.site.register(FoodItem,FoodItemAdmin)