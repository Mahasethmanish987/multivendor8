from django.shortcuts import render,redirect
from .models import User
from .forms  import UserForm
from django.contrib import messages
from django.contrib.auth import authenticate,login ,logout
from .utils import send_verification_email ,redirectUrl
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_decode
from django.contrib.auth.decorators import login_required ,user_passes_test
from django.db import transaction
from vendor.views import checkCustomer,checkVendor

# Create your views here.

def userRegister(request):
    if request.user.is_authenticated:
       messages.success(request,'User is already logged in ')
       return redirect('myapp:index')
    if request.method=='POST':
       form=UserForm(request.POST)
       if form.is_valid():
            with transaction.atomic():
                try:
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
                        user.role = User.CUSTOMER
                        user.save()

                        # Send verification email
                        mail_subject = 'Please activate your account'
                        mail_template = 'accounts/account_verification.html'
                        send_verification_email(request, user, mail_subject, mail_template)

                        messages.success(request, 'User registered successfully')
                        return redirect('myapp:index')
                    else:
                        messages.error(request, 'Passwords do not match')
                except Exception as e:
                    # Log or print the error for debugging
                    print(f"Error during user registration: {e}")
                    messages.error(request, 'An error occurred during registration. Please try again.')
                    return  redirect('myapp:index')

       else:
        context={'form':form}

    else:
     form=UserForm()
     context={
      'form':form
   }
    return render(request,'accounts/userRegister.html',context)


def login_view(request):
  if request.user.is_authenticated:
       messages.success(request,'User is already logged in ')
       return redirect('myapp:index')
  if request.method=='POST':
    username=request.POST['username']
    password=request.POST['password']
    user=authenticate(username=username,password=password)
    if user is not None:
       login(request,user)
       messages.success(request,'User has been logged in ')
       return redirect('account:myAccount')
    else:
       messages.error(request,'Invalid Credentials')
       return redirect('account:login')

  return render(request,'accounts/login.html')

def logout_view(request):
  if not  request.user.is_authenticated:
       messages.success(request,'User is already logout in ')
       return redirect('myapp:index')
  logout(request)
  messages.success(request,'User has been successfully logout')
  return redirect('myapp:index')
@login_required(login_url='account:login')
def myAccount(request):
   redirectu=redirectUrl(request)
   if redirectu=='admin:index':
      return redirect('admin:index')
   elif redirectu=='account:customerDashboard':
      return redirect('customer:customerDashboard')
   else:
      return redirect('vendor:vendorDashboard')




def activate(request,uid,token):
   try:
      id=urlsafe_base64_decode(uid).decode()
      user=User.objects.get(pk=id)


   except User.DoesNotExist:
      user=None
   except(TypeError,ValueError,OverflowError):
      user=None

   if user is not None and default_token_generator.check_token(user,token):
     user.is_active=True
     user.save()
     messages.info(request,'User is activated')
     return redirect('account:login')
   else:
      messages.error(request,'Invalid Link')
      return redirect('account:userRegister')




def forgot_password(request):
   if request.method=='POST':
      email=request.POST['email']
      if User.objects.filter(email=email).exists():
         user=User.objects.get(email=email)
         mail_subject='please click the link to reset the password'
         mail_template='accounts/email_forgot_password.html'
         send_verification_email(request,user,mail_subject,mail_template)
         messages.success(request,'Password reset email has sent successfully')
         return redirect('myapp:index')
      else:
         messages.error(request,'Invalid Email')
         return render(request,'accounts/forgot_password.html')

   return render(request,'accounts/forgot_password.html')

def reset_password(request,uid,token):
   try:
      id=urlsafe_base64_decode(uid).decode()
      user=User.objects.get(id=id)
   except User.DoesNotExist:
      user=None
   except (TypeError,OverflowError,ValueError):
      user=None
   if user is not None and default_token_generator.check_token(user,token):
      request.session['id']=id
      messages.info(request,'Please reset your password')
      return redirect('account:password_reset_done')
   else:
      messages.error(request,'Invalid Link')
      return redirect('account:forgot_password')


def password_reset_done(request):

   if request.method=='POST':
      password=request.POST['password']
      confirm_password=request.POST['confirm_password']
      if password==confirm_password:
         pk=request.session.get('id')
         if pk is None:

            messages.error(request,'User not found')
            return redirect('account:forgot_password')
         else:
            try:
               user=User.objects.get(id=pk)
            except User.DoesNotExist:
               user=None
            if user is not None:

                user.set_password(password)
                user.is_active=True
                user.save()
                messages.success(request,'password reset done')
                return redirect('account:login')
            else:
               messages.error(request,'User not found')
               return redirect('account:forgot_password')
      else:
         messages.info(request,'Password and confirm password does not match')
         return render(request,'accounts.password_reset_done.html')
   else:
      return render(request,'accounts/password_reset_done.html')