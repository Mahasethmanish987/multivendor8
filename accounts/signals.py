from allauth.account.signals import user_signed_up
from django.db.models.signals import post_save
from django.dispatch import receiver 
from .models import User,UserProfile 


@receiver(post_save,sender=User)
def post_save_create_profile_receiver(sender,instance,created,**kwargs):
    if created:
        UserProfile.objects.create(user=instance)
    else:
        try:
            profile=UserProfile.objects.get(user=instance)
            profile.save()
        except:
            UserProfile.objects.create(user=instance)        



@receiver(user_signed_up)
def activate_user_on_signup(request, user, **kwargs):
    # Automatically activate the user
    if not user.is_active:
        user.is_active = True
        user.save()
        

