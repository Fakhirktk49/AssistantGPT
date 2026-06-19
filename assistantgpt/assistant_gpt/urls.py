from django.urls import path
from assistant_gpt.views import home,login,register,activate_account,loginview,create_chat,chats,load_chat,url_chat
from django.contrib.auth.views import LogoutView

urlpatterns=[
    path('home/',home,name='home'),
    path('login/',loginview,name='login'),
    path('register/',register,name='register'),
    path('activate_account/<str:uid>/<str:token>/',activate_account,name='activate_account'),
    path('logout/',LogoutView.as_view(),name='logout'),
    path('create_chat/',create_chat,name='create_chat'),
    path('chats/',chats,name='chats'),
    path('c/<str:chat_id>/',load_chat,name='load_chat'),
    path('chat/<str:chat_id>/',url_chat,name='url_chat') 

]