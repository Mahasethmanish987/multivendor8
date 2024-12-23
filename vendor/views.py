from django.shortcuts import render,redirect
from .models import Vendor,OpeningHour
from accounts.forms import UserForm
from .forms import VendorForm,OpeningHourForm
from accounts.models import User ,UserProfile
from django.template.defaultfilters import slugify
from django.contrib import messages
from accounts.utils import send_verification_email
from django.db import transaction
from django.contrib.auth.decorators import login_required,user_passes_test
from accounts.forms import UserProfileForm
from django.shortcuts import get_object_or_404
# Create your views here.
from django.core.exceptions import PermissionDenied
import logging
from django.http import Http404
from menu.forms import CategoryForm,FoodItemForm
from django.template.defaultfilters import slugify
from menu.models import Category,FoodItem
from urllib.parse import urlparse
from django.http import JsonResponse
from django.db import IntegrityError

logger=logging.getLogger(__name__)
def getVendor(request):
    user=request.user
    if not user.is_authenticated:
        logger.warning(f'Unauthorized access attempy by an unauthenticated user')
        raise PermissionDenied('Authenticated Required')
    try:
        return Vendor.objects.get(user=user)
    except Vendor.DoesNotExist:
        logger.error(f"vendor profile not found for user:{user.username}")
        raise Http404('vendor not found')

def checkVendor(user):

    if user.role==1:
        return True
    else:
        raise PermissionDenied

def checkCustomer(user):

    if user.role==2:
        return True
    else:
        raise PermissionDenied
@login_required(login_url='account:login')
@user_passes_test(checkVendor)
def vendorDashboard(request):
    return render(request,'vendor/vendorDashboard.html')
def registerVendor(request):
    if request.method=='POST':
        # form,v_form
        form=UserForm(request.POST)
        v_form=VendorForm(request.POST,request.FILES)

        if form.is_valid() and v_form.is_valid():

                try:
                   with transaction.atomic():
                    first_name = request.POST.get('first_name')
                    last_name = request.POST.get('last_name')
                    email = request.POST.get('email')
                    username = request.POST.get('username')
                    phone_number = request.POST.get('phone_number')
                    password = request.POST.get('password')
                    confirm_password = request.POST.get('confirm_password')

                    if password == confirm_password:
                        # Create user
                        user = User.objects.create_user(
                            first_name=first_name,
                            last_name=last_name,
                            username=username,
                            email=email,
                            password=password,
                            phone_number=phone_number
                        )
                        user.role = User.RESTAURANT
                        user.save()

                        # Send verification email
                        mail_subject = 'Please activate your account'
                        mail_template = 'accounts/account_verification.html'
                        send_verification_email(request, user, mail_subject, mail_template)
                        vendor=v_form.save(commit=False)
                        vendor.user=user
                        user_profile=UserProfile.objects.get(user=user)
                        vendor.user_profile=user_profile
                        vendor.vendor_slug=slugify(vendor.vendor_name)+'-'+str(user.id)
                        vendor.save()

                        messages.success(request, 'User registered successfully')
                        return redirect('myapp:index')
                    else:
                        messages.error(request, 'Passwords do not match')
                except Exception as e:
                    # Log or print the error for debugging
                    print(f"Error during user registration: {e}")
                    messages.error(request, 'An error occurred during registration. Please try again.')
                    return redirect('myapp:index')



        else:
            context={
                'form':form,
                'v_form':v_form
            }

    else:
        form=UserForm()
        v_form=VendorForm()
        context={
            'form':form,
            'v_form':v_form
        }

    return render(request,'vendor/registerVendor.html',context)

@login_required(login_url='account:login')
@user_passes_test(checkVendor,login_url='account:login')
def vprofile(request):
    vendor=getVendor(request)
    try:
        profile=UserProfile.objects.get(user=request.user)
    except UserProfile.DoesNotExist:
        profile=UserProfile.objects.create(user=request.user)


    if request.method=='POST':
        user_profile=UserProfileForm(request.POST,request.FILES,instance=profile)
        vendor_profile=VendorForm(request.POST,request.FILES,instance=vendor)
        if user_profile.is_valid() and vendor_profile.is_valid():
            user_profile.save()
            vendor_profile.save()
            messages.success(request,'settings update')
            return redirect('vendor:vprofile')
        else:
            context={
                'user_profile':user_profile,
                'vendor_profile':vendor_profile,
                'vendor':vendor,
                'profile':profile

            }
            return render(request,'vendor/vprofile.html',context)

    else:
        user_profile=UserProfileForm(instance=profile)
        vendor_profile=VendorForm(instance=vendor)
        context={
            'user_profile':user_profile,
            'vendor_profile':vendor_profile,
            'vendor':vendor,
            'profile':profile
        }
        return render(request,'vendor/vprofile.html',context)

@login_required(login_url='account:login')
@user_passes_test(checkVendor,login_url='account:login')
def menu_builder(request):
    vendor=getVendor(request)
    categories=Category.objects.filter(vendor=vendor)
    context={
        'categories':categories
    }
    return render(request,'vendor/menu_builder.html',context)
@login_required(login_url='account:login')
@user_passes_test(checkVendor,login_url='account:login')
def fooditem_by_category(request,id):
    vendor=getVendor(request)
    category=get_object_or_404(Category,pk=id)
    fooditems=FoodItem.objects.filter(vendor=vendor,category=category)
    context={
        'fooditems':fooditems,
        'category':category
    }
    return render(request,'vendor/fooditem_by_category.html',context)


@login_required(login_url='account:login')
@user_passes_test(checkVendor,login_url='account:login')
def add_category(request):
    if request.method=='POST':
        form=CategoryForm(request.POST)
        if form.is_valid():
            category=form.save(commit=False)
            category.vendor=getVendor(request)
            category.save()
            category.category_slug=slugify(category.category_name)+'-'+str(category.id)
            messages.success(request,'Category added')
            return redirect('vendor:menu_builder')
        else:
            context={
                'form':form
            }
            return render(request,'vendor/add_category.html',context)
    else:
        form=CategoryForm()
        context={
            'form':form
        }
    return render(request,'vendor/add_category.html',context)
@login_required(login_url='account:login')
@user_passes_test(checkVendor,login_url='account:login')
def edit_category(request,id):
    try:
       category=get_object_or_404(Category,id=id,vendor=getVendor(request))
    except Http404:
          messages.error(request,'the category does not exist you do not have permission to edit these category')
          return redirect('vendor:menu_builder')



    if request.method=='POST':
        form=CategoryForm(request.POST,instance=category)
        if form.is_valid():
            try:
               category=form.save(commit=False)
               category.vendor=getVendor(request)

               category.slug=slugify(category.category_name)+'-'+str(category.id)
               category.save()
               messages.success(request,'Your category has been updated')
               return redirect('vendor:menu_builder')
            except Exception as e:
                messages.error(request,f'An error occured while updating the category:{str(e)}')
                context={
                'form':form
                        }
                return render(request,'vendor/edit_category.html',context)
        else:
            context={
                'form':form
            }
            return render(request,'vendor/edit_category.html',context)
    else:
        form=CategoryForm(instance=category)
        context={
            'form':form
        }
        return render(request,'vendor/edit_category.html',context)


@login_required(login_url='account:login')
@user_passes_test(checkVendor,login_url='account:login')
def delete_category(request,id):

    try:
        category=get_object_or_404(Category,id=id,vendor=getVendor(request))
        category.delete()
        messages.success(request,'Category is successfully deleted')
    except Http404:
        messages.error(request,'The category does not exist for you do not have permission to delete these category')
    except Category.DoesNotExist:
        messages.error(request,'No such category exist')

    except Exception as e:
        messages.error(request,f'An error occured while updating the category:{str(e)}')

    return redirect('vendor:menu_builder')

def add_food(request):


    # print(request.build_absolute_uri())
    if request.method=='POST':
        form=FoodItemForm(request.POST,request.FILES)
        if form.is_valid():
            foodtitle=form.cleaned_data['food_title']
            food=form.save(commit=False)
            food.vendor=getVendor(request)
            food.slug=slugify(foodtitle)
            food.save()
            messages.success(request,'Food items has updated succesfully')
            return redirect('vendor:food_items_by_category' ,food.category.id)
        else:
            return render(request,'vendor/add_food.html',{'form':form})
    else:

      form=FoodItemForm()
      referrer_url = request.META.get('HTTP_REFERER', None)
      if referrer_url is not None:
         if "/menu_builder/fooditem_by_category/" in referrer_url:
          parsed_url=urlparse(referrer_url)

          path=parsed_url.path

          segments=path.strip("/").split("/")
          print(segments[-1])
          category=Category.objects.get(id=segments[-1])
          form.fields['category'].queryset=Category.objects.filter(vendor=getVendor
                                                                   (request),id=category.id)
          return render(request,'vendor/add_food.html',{'form':form})

      form.fields['category'].queryset=Category.objects.filter(vendor=getVendor(request))
      return render(request,'vendor/add_food.html',{'form':form})

def edit_food(request,id):

    food=get_object_or_404(FoodItem,pk=id)
    if request.method=='POST':
        form=FoodItemForm(request.POST,request.FILES,instance=food)
        if form.is_valid():
            foodtitle=form.cleaned_data['food_title']
            food1=form.save(commit=False)
            food1.vendor=getVendor(request)
            food1.slug=slugify(foodtitle)
            food.save()
            messages.success(request,'Food items saved successfully')
            return redirect('vendor:food_items_by_category',food.category.id)
        else:
            return render(request,'vendor/edit_form.html',{'form':form,'food':food})
    else:
        form=FoodItemForm(instance=food)
    return render(request,'vendor/edit_food.html',{'form':form,'food':food})


def delete_food(request,pk):
    food=FoodItem.objects.get(pk=pk)
    food.delete()
    messages.success(request,'food items deleted successfuly')
    return redirect('vendor:food_items_by_category',food.category.id)

@login_required(login_url='account:login')
@user_passes_test(checkVendor)
def opening_hours(request):
    form=OpeningHourForm()
    opening_hours=OpeningHour.objects.filter(vendor=getVendor(request))
    context={
        'form':form,
        'opening_hours':opening_hours
    }
    return render(request,'vendor/opening_hours.html',context)

def add_opening_hours(request):
    if not request.user.is_authenticated:
        return JsonResponse({'status':'Failed','message':'User should be authenticated'})

    if request.headers.get('x-requested-with')!='XMLHttpRequest':
        return JsonResponse({'status':'Failed','message':'Invalied Request'})

    day=request.POST['day']
    from_hour=request.POST['from_hour']
    to_hour=request.POST['to_hour']
    is_closed=request.POST['is_closed']

    try:
        hour=OpeningHour.objects.create(vendor=getVendor(request),day=day,from_hour=from_hour,to_hour=to_hour,is_closed=is_closed)

        if hour:
            day=OpeningHour.objects.get(id=hour.id)
            if day.is_closed:
                response={'status':'success','id':hour.id,'day':day.get_day_display(),'is_closed':'closed'}

            else:
                response={'status':'success','id':hour.id,'day':day.get_day_display(),'from_hour':day.from_hour,'to_hour':day.to_hour}

            
            return JsonResponse(response)
    except IntegrityError as e:
        response={'status':'Failed','message':from_hour+'-'+to_hour+'already exists','error':str(e)}



def delete_opening_hours(request,pk):
    if not request.user.is_authenticated:
        return JsonResponse({'status':'login_required','message':'User should be authenticated'})

    if request.headers.get('x-requested-with')!='XMLHttpRequest':
        return JsonResponse({'status':'Failed','message':'Invalied Request'})

    hour=get_object_or_404(OpeningHour,pk=pk)
    hour.delete()
    return JsonResponse({'status':'success','id':pk})
