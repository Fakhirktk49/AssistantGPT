from django.db import models
from django.contrib.auth.models import AbstractBaseUser,BaseUserManager
import uuid
# Create your models here.
PLAN_CHOICES=(('Free','Free'),
              ('Premium',"Premium"))

ROLE_CHOICES=(('system','system'),
              ('user','user'))


class User(BaseUserManager):
    def create_user(self,email,password=None):
        if not email:
            raise ValueError("Email is required.")
        user=self.model(email=self.normalize_email(email))
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self,email,password=None,**extra_fields):
        extra_fields.setdefault('is_active',True)
        extra_fields.setdefault('is_superuser',True)
        
        user=self.create_user(email=email,password=password)
        user.is_active=True
        user.is_superuser=True
        user.is_staff=True
        user.save(using=self._db)
        return user
        

class CustomUser(AbstractBaseUser):
    email=models.EmailField(max_length=255,unique=True)
    name=models.CharField(max_length=255)
    city=models.CharField(max_length=255,blank=True)
    phone=models.IntegerField(blank=True,null=True)
    country=models.CharField(max_length=255,blank=True)
    plan=models.CharField(choices=PLAN_CHOICES,default='Free')
    profile_image=models.ImageField(blank=True,upload_to='profile-images/')

    is_active=models.BooleanField(default=0)
    is_staff=models.BooleanField(default=0)
    is_superuser=models.BooleanField(default=0)

    created_at=models.DateTimeField(auto_now_add=True,null=True)
    updated_at=models.DateTimeField(auto_now=True,null=True)

    USERNAME_FIELD='email'

    objects=User()

    def __str__(self):
        return self.email
    
    def has_perm(self,obj=None):
        return self.is_superuser
    
    def has_module_perms(self,app_label):
        return self.is_superuser
    

class Chat(models.Model):
    user=models.ForeignKey(CustomUser,on_delete=models.CASCADE)
    id=models.UUIDField(primary_key=True,default=uuid.uuid4,editable=False)
    title=models.CharField(max_length=255)

class MessagesTable(models.Model):
    chat=models.ForeignKey(Chat,on_delete=models.CASCADE)
    msg=models.TextField()
    role=models.CharField(choices=ROLE_CHOICES)

    
    
    
