from django.urls import path
from . import views

app_name='order'
urlpatterns=[
    path('place_order/',views.place_order,name='place_order'),
    path('esewacredentials/',views.esewacredentials,name='esewacredentials'),
    path('handle_paypal/',views.handle_paypal,name='handle_paypal'),
    path('handle_esewa/',views.handle_esewa,name='handle_esewa'),
    path('order_complete/',views.order_complete,name='order_complete')


]