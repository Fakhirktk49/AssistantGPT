from django.contrib import admin
from .models import MessagesTable,CustomUser
from django.contrib.auth.admin import UserAdmin
# Register your models here.

admin.site.register(MessagesTable)

class CustomUserAdmin(UserAdmin):
    list_display=['email','name','city']

    fieldsets=[('Personal Info',{'fields':['email','name','city','phone','country','profile_image']}),('Billing Info',{'fields':['plan']}),('User Status',{'fields':['is_active','is_staff','is_superuser']})]
     
    add_fieldsets=((None,{'classes':'wide','fields':['email','password1','password2']}),
                   )
    
    
   
    ordering=['name']
    filter_horizontal=[]
    search_fields=['name','email']
    list_filter=['phone']

admin.site.register(CustomUser,CustomUserAdmin)
