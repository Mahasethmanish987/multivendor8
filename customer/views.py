from django.shortcuts import render,redirect ,get_object_or_404
from django.contrib.auth.decorators import login_required ,user_passes_test
from vendor.views import checkCustomer
from accounts.forms import UserProfileForm,UserInfoForm
from accounts.models import User,UserProfile
from django.contrib import messages
# Create your views here.
@login_required(login_url='account:login')
@user_passes_test(checkCustomer)
def customerDashboard(request):
    return render(request,'customer/customerDashboard.html')
@login_required(login_url='account:login')
@user_passes_test(checkCustomer)
def cprofile(request):
    profile=get_object_or_404(UserProfile,user=request.user)

    if request.method=='POST':
        profile_form=UserProfileForm(request.POST,request.FILES,instance=profile)
        user_form=UserProfileForm(request.POST,instance=request.user)
        if profile_form.is_valid() and user_form.is_valid():
            profile_form.save()
            user_form.save()
            messages.success(request,'profile updated successfully')
            return redirect('customer:cprofile')

        else:
            context={
            'profile_form':profile_form,
            'user_form':user_form,
            'profile':profile
            }
            return render(request,'customer/cprofile.html',context)

    else:
        profile_form=UserProfileForm(instance=profile)
        user_form=UserInfoForm(instance=request.user)
        context={
            'profile_form':profile_form,
            'user_form':user_form,
            'profile':profile
        }
        return render(request,'customer/cprofile.html',context)