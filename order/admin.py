from django.contrib import admin

# Register your models here.
from .models import Payment,Order,OrderedFood
class OrderedFoodInline(admin.TabularInline):
   model=OrderedFood
   readonly_fields=('order','payment','user','fooditem','quantity')
   extra=0

class paymentAdmin(admin.ModelAdmin):
   fields=('user','transaction_id','payment_method','status')
   inlines=[OrderedFoodInline]

class orderAdmin(admin.ModelAdmin):
   list_display=('order_number','first_name','phone','email','total','payment_method','order_place_to','status')
   inlines=[OrderedFoodInline]

admin.site.register(Order,orderAdmin)
admin.site.register(Payment,paymentAdmin)
admin.site.register(OrderedFood)
