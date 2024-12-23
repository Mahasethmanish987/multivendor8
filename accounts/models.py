from django.db import models
from django.contrib.auth.models import BaseUserManager,AbstractBaseUser
from django.contrib.gis.db import models as gismodels
from django.contrib.gis.geos import Point
# Create your models here.

class UserManager(BaseUserManager):

    def create_user(self,first_name,last_name,username,email,phone_number,password=None):
         if not email:
              raise ValueError('Email field must be provided')
         if not username:
              raise ValueError('Username should be provided')

         user=self.model(email=self.normalize_email(email),first_name=first_name,last_name=last_name,username=username,phone_number=phone_number)
         user.set_password(password)
         user.save()
         return user

    def create_superuser(self,email,first_name,last_name,username,password,phone_number):
              user=self.create_user(email=email,first_name=first_name,last_name=last_name,username=username,password=password,phone_number=phone_number)
              user.is_active=True
              user.is_staff=True
              user.is_admin=True
              user.is_superuser=True
              user.save()
              return user

class User(AbstractBaseUser):
      RESTAURANT=1
      CUSTOMER=2
      CHOICES=(
            (RESTAURANT,'Restaurant'),
            (CUSTOMER,'Customer')
      )
      email=models.EmailField(max_length=50,unique=True)
      username=models.CharField(max_length=50,unique=True)
      first_name=models.CharField(max_length=50)
      last_name=models.CharField(max_length=50)
      phone_number=models.CharField(max_length=20)
      role=models.PositiveSmallIntegerField(choices=CHOICES,blank=True,null=True)


      created_at=models.DateTimeField(auto_now_add=True)
      last_login=models.DateTimeField(auto_now=True)
      modified_at=models.DateTimeField(auto_now=True)

      is_active=models.BooleanField(default=False)
      is_staff=models.BooleanField(default=False)
      is_admin=models.BooleanField(default=False)
      is_superuser=models.BooleanField(default=False)

      USERNAME_FIELD='email'
      REQUIRED_FIELDS=['username','first_name','last_name','phone_number']
      objects=UserManager()


      def __str__(self):
            return self.email

      def has_perm(self,perm,obj=None):
            return self.is_admin
      def has_module_perms(self,app_label):
            return True

      def get_role(self):
            if self.role==self.RESTAURANT:
                  return 'Restaurant'

            elif self.role==self.CUSTOMER:
                  return 'Customer'
            else:
                  return 'admin'



class UserProfile(models.Model):
      user=models.OneToOneField(User,on_delete=models.CASCADE)
      profile_picture=models.ImageField(upload_to='users/profile_picture/',blank=True,null=True)
      cover_photo=models.ImageField(upload_to='users/cover_photo/',blank=True,null=True)
      address=models.CharField(max_length=100,null=True,blank=True)
      state=models.CharField(max_length=100,blank=True,null=True)
      country=models.CharField(max_length=100,blank=True,null=True)
      pin_code=models.CharField(max_length=100,blank=True,null=True)
      latitude=models.CharField(max_length=50,null=True,blank=True)
      longitude=models.CharField(max_length=50,null=True,blank=True)
      location=gismodels.PointField(blank=True,null=True,srid=4326)


      created_at=models.DateTimeField(auto_now_add=True)
      modified_at=models.DateTimeField(auto_now=True)

      def __str__(self):
            return self.user.email

      def save(self,*args,**kwargs):
            if self.latitude and self.longitude:
                  self.location=Point(float(self.longitude),float(self.latitude))

            super(UserProfile,self).save(*args,**kwargs)