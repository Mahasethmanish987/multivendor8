from django.urls import path 
from . import views 

app_name='marketplace'

urlpatterns=[
    path('',views.marketplace,name='marketplace'),
    path('<slug:vendor_slug>/',views.vendor_detail,name='vendor_detail'),

    path('add_to_cart/<int:id>',views.add_to_cart,name='add_to_cart'),
    path('decrease_cart/<int:id>',views.decrease_cart,name='decrease_cart'),
    path('delete_cart/<int:id>/',views.delete_cart,name='delete_cart'),
   

]