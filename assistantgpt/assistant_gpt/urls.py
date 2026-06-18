from django.urls import path
from assistant_gpt.views import home,login,register

urlpatterns=[
    path('home/',home,name='home'),
    path('login/',login,name='login'),
    path('register/',register,name='register')
]