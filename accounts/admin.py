from django.contrib import admin
from .models import User,UserProfile

# Register your models here.

class UserAdmin(admin.ModelAdmin):
    list_display=('username','email','role','is_active','created_at','last_login')
    list_editable=('is_active',)
readonly_fields=('password',)
class UserProfileAdmin(admin.ModelAdmin):
    list_display=('user','address')
admin.site.register(User,UserAdmin)
admin.site.register(UserProfile,UserProfileAdmin)
