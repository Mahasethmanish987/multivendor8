from django.urls import path
from . import views

app_name='vendor'
urlpatterns=[
    path('',views.vendorDashboard,name='vendorDashboard'),
    path('registerVendor/',views.registerVendor,name='registerVendor'),
    path('vprofile/',views.vprofile,name='vprofile'),
    path('menu_builder',views.menu_builder,name='menu_builder'),
    path('menu_builder/fooditem_by_category/<int:id>/',views.fooditem_by_category,name='food_items_by_category'),


    path('menu_builder/add_category',views.add_category,name='add_category'),
    path('menu_builder/edit_category/<int:id>/',views.edit_category,name='edit_category'),
    path('menu_builder/delete_category/<int:id>/',views.delete_category,name='delete_category'),

    path('menu_builder/add_food/',views.add_food,name='add_food'),
    path('menu_builder/edit_food/<int:id>',views.edit_food,name='edit_food'),
    path('menu_builder/delete_food/<int:id>',views.delete_food,name='delete_food'),

    path('opening_hours/',views.opening_hours,name='opening_hours'),
    path('opening_hours/add/',views.add_opening_hours,name='add_opening_hour'),
    path('opening_hours/delete/<int:pk>/',views.delete_opening_hours,name='delete_opening_hour'),



]