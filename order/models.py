from django.db import models

# Create your models here.
from accounts.models import User
from vendor.models import Vendor
from menu.models import FoodItem
class Payment(models.Model):
    PAYMENT_METHOD=(
        ('paypal','paypal'),
        ('khalti','khalti'),
        ('esewa','esewa'),
    )
    user=models.ForeignKey(User,on_delete=models.CASCADE)
    transaction_id=models.CharField(max_length=100)
    payment_method=models.CharField(choices=PAYMENT_METHOD)
    amount=models.CharField(max_length=10)
    status=models.CharField(max_length=100)
    created_at=models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.transaction_id

class Order(models.Model):
    STATUS=(
        ('new','new'),
        ('accepted','accepted'),
        ('completed','completed'),
        ('cancelled','cancelled'),
    )
    user=models.ForeignKey(User,on_delete=models.CASCADE)
    payment=models.ForeignKey(Payment,on_delete=models.CASCADE,blank=True,null=True)
    vendors=models.ManyToManyField(Vendor,blank=True)
    order_number=models.CharField(max_length=50)
    first_name=models.CharField(max_length=50)
    last_name=models.CharField(max_length=50)
    phone=models.CharField(max_length=20,blank=True)
    email=models.EmailField(max_length=50)
    address=models.CharField(max_length=200)
    country=models.CharField(max_length=50,blank=True)
    state=models.CharField(max_length=50,blank=True)
    pin_code=models.CharField(max_length=50,blank=True)

    total=models.CharField(max_length=10)
    tax_data=models.JSONField(blank=True)
    total_tax=models.FloatField()
    total_data=models.JSONField(blank=True,null=True)
    payment_method=models.CharField(max_length=25)
    status=models.CharField(choices=STATUS)
    is_ordered=models.BooleanField(default=False)
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now=True)


    def order_place_to(self):
        return " ,".join([str(i) for i in self.vendors.all()])
    def __str__(self):
        return self.order_number

class OrderedFood(models.Model):
    order=models.ForeignKey(Order,on_delete=models.CASCADE)
    payment=models.ForeignKey(Payment,on_delete=models.SET_NULL,blank=True,null=True)
    user=models.ForeignKey(User,on_delete=models.CASCADE)
    fooditem=models.ForeignKey(FoodItem,on_delete=models.CASCADE)
    quantity=models.IntegerField()
    price=models.FloatField()
    amount=models.FloatField()
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.fooditem.food_title

