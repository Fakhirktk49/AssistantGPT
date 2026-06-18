from django.urls import path
from assistant_gpt.views import chat

urlpatterns=[
    path('chat/',chat,name='chat')
]