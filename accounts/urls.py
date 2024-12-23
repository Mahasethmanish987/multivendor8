from . import views
from django.urls import path


app_name='account'

urlpatterns=[
       path('userRegister/',views.userRegister,name='userRegister'),
       path('login/',views.login_view,name='login'),
       path('logout/',views.logout_view,name='logout'),
       path('myAccount',views.myAccount,name='myAccount'),
       path('activate/<uid>/<token>/',views.activate,name='activate'),
      

       path('forgot_password/',views.forgot_password,name='forgot_password'),
       path('reset_password/<uid>/<token>/',views.reset_password,name='reset_password'),
       path('password_reset_done/',views.password_reset_done,name='password_reset_done'),
]