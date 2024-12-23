from django.shortcuts import render,get_object_or_404,redirect
from vendor.models import Vendor
from menu.models import Category,FoodItem
from django.db.models import Prefetch
from django.http import JsonResponse
from .models import Cart
from .context_processors import get_cart_counter,get_cart_amount
from django.contrib.auth.decorators import login_required ,user_passes_test
from django.db.models import Q
from django.contrib.gis.geos import GEOSGeometry
from django.contrib.gis.measure import D
from django.contrib.gis.db.models.functions import Distance
from accounts.models import UserProfile
from order.forms import OrderForm
# Create your views here.
def marketplace(request):
    vendors=Vendor.objects.filter(user__is_active=True,is_approved=True)
    vendor_count=vendors.count()
    context={
        'vendors':vendors,
        'vendor_count':vendor_count
    }
    return render(request,'marketplace/marketplace.html',context)

def vendor_detail(request,vendor_slug):
    vendor_instance=get_object_or_404(Vendor,vendor_slug=vendor_slug)
    categories=Category.objects.filter(vendor=vendor_instance).prefetch_related(
        Prefetch('fooditem_set',queryset=FoodItem.objects.filter(is_available=True))
    )
    context={
        'Vendor':vendor_instance,
        'categories':categories
    }
    return render(request,'marketplace/vendor_detail.html',context)

def add_to_cart(request,id):

    if not request.user.is_authenticated:
        return JsonResponse({'status':'login_required','message':'Please login'})
    if request.headers.get('x-requested-with')!='XMLHttpRequest':
        return JsonResponse({'status':'Failed','message':'Invalid request'})

    try:
        fooditem=FoodItem.objects.get(id=id)

        try:

            cart=Cart.objects.get(user=request.user,fooditem=fooditem)
            cart.quantity+=1
            cart.save()

            message='cart items quantity increased'
        except Cart.DoesNotExist:
            cart=Cart.objects.create(user=request.user,fooditem=fooditem,quantity=1)
            message='cart item added to cart'
        resonse_data={
            'status':'success',
            'message':message,
            'quantity':cart.quantity,
            'get_cart_count':get_cart_counter(request),
            'cart_amount':get_cart_amount(request)
        }
        return JsonResponse(resonse_data)
    except:
        return JsonResponse({'status':'Failed','message':'No such food item exist'})


def decrease_cart(request,id):
    if not request.user.is_authenticated:
        return JsonResponse({'status':'login_required','message':'Please login'})
    if request.headers.get('x-requested-with')!='XMLHttpRequest':
        return JsonResponse({'status':'Failed','message':'Invalid request'})

    try:
        fooditem=FoodItem.objects.get(id=id)
        try:
            cart=Cart.objects.get(user=request.user,fooditem=fooditem)
            if cart.quantity >1:
                cart.quantity-=1
                cart.save()
            else:
                cart.delete()
                cart.quantity=0
            return JsonResponse({'status':'success','message':'cart items decreased','quantity':cart.quantity,'get_cart_count':get_cart_counter(request),'cart_amount':get_cart_amount(request)})
        except:
            return JsonResponse({'status':'Failed','message':'No such cart exist'})

    except:
        return JsonResponse({'status':'Failed','message':'No such fooditem exist'})
@login_required(login_url='account:login')
def cart(request):
    cart_items=Cart.objects.filter(user=request.user)
    context={
        'cart_items':cart_items
    }
    return render(request,'marketplace/cart.html',context)
@login_required(login_url='account:login')
def delete_cart(request,id):
    if not  request.user.is_authenticated:
        return JsonResponse({'status':'login_required','message':'please login'})
    if request.headers.get('x-requested-with')!='XMLHttpRequest':
        return JsonResponse({'status':'success','message':'Invalid Request'})
    try:
        cart_item=get_object_or_404(Cart,user=request.user,id=id)
        cart_item.delete()
        return JsonResponse({'status':'success','message':'Item deleted successfully','cart_counter':get_cart_counter(request),'cart_amount':get_cart_amount(request)})
    except Exception as e:
        return JsonResponse({'status':'Failed','message':f'Error:{str(e)}'}, status=500)


def search(request):

    if request.method=='POST':
        address=request.POST['address']
        rest_name=request.POST['rest_name']
        lat=request.POST['lat']
        lng=request.POST['lng']
        radius=request.POST['radius']
        print(lat,lng,radius)

        fetch_vendor_by_fooditems=FoodItem.objects.filter(food_title__icontains=rest_name,is_available=True).values_list('vendor',flat=True)

        vendors=Vendor.objects.filter(Q(id__in=fetch_vendor_by_fooditems)|Q(vendor_name__icontains=rest_name))

        if lat and lng and radius :

            pnt=GEOSGeometry('POINT(%s %s)'%(lng,lat))
            vendors=Vendor.objects.filter(Q(id__in=fetch_vendor_by_fooditems)|Q(vendor_name__icontains=rest_name,is_approved=True,user__is_active=True),user_profile__location__distance_lte=(pnt,D(km=radius))).annotate(distance=Distance("user_profile__location",pnt)).order_by('distance')


            for v in vendors:
                v.kms=round(v.distance.km,1)


        vendor_count=vendors.count()
        context={
            'vendors':vendors,
            'vendor_count':vendor_count,
            'source_location':address,

        }
        return render(request,'marketplace/marketplace.html',context)

@login_required(login_url='account:login')
def checkout(request):
    cart_items=Cart.objects.filter(user=request.user).order_by('created_at')
    cart_count=cart_items.count()
    user_profile=UserProfile.objects.get(user=request.user)

    if cart_count<=0:
        return redirect('marketplace:marketplace')

    default={'first_name':request.user.first_name,
             'last_name':request.user.last_name,
             'email':request.user.email,
             'phone':request.user.phone_number,
             'address':user_profile.address,
             'country':user_profile.country,
             'state':user_profile.state,
             'pin_code':user_profile.pin_code}

    form=OrderForm(initial=default)
    context={
        'form':form,
        'cart_items':cart_items
    }
    return render(request,'marketplace/checkout.html',context)