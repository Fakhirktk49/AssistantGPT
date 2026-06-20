from django.shortcuts import render
import json
from openai import OpenAI
from django.http import JsonResponse
from .forms import RegisterForm
from django.contrib import messages
from django.utils.http import urlsafe_base64_decode,urlsafe_base64_encode
from django.utils.encoding import force_bytes,force_str
from django.urls import reverse
from django.conf import settings
from django.contrib.auth.tokens import default_token_generator
from django.shortcuts import redirect
from django.contrib.auth import authenticate,login
from .utils import email_sender
from core.models import CustomUser,Chat,MessagesTable
import json
from decouple import config
from django.contrib.auth.decorators import login_required
from django.utils.html import escape
import uuid
from django.views.decorators.csrf import ensure_csrf_cookie


# Create your views here.
@ensure_csrf_cookie
def home(request):
    if not request.user.is_authenticated:
        if request.method == 'POST':
            try:
                if 'user_data' in request.session:
                    data=json.loads(request.body)
                    prompt=data['message']
                    user_data=request.session.get('user_data')
                    for key,values in user_data.items():
                        question,response=values.split('_')
                        messages.append({'role':'user','content':question})
                        messages.append({'role':'assistant','content':response})

                    messages.append({'role':'user','content':prompt})
                    print(messages)         
                    client=OpenAI(api_key=config('API_KEY'))
                    responses=client.chat.completions.create(model='gpt-5.4-mini',
                                                messages=messages,
                                                temperature=0,
                                                n=1,
                                                stop=None,
                                                )

                    response=responses.choices[0].message.content
                    #json_result={"label":response}
                    user_data=request.session.get('user_data')
                    id=list(user_data.keys())[-1]
                    id=int(id)
                    id +=1
                    user_data[id]=f'{prompt}_{response}'
                    request.session['user_data']=user_data
                    updated_session=request.session.get('user_data')
                    print(updated_session)
                    return JsonResponse({'response':response})
            except Exception as e:
                        print(e)
                        error={'label':'when session some exception occured.'}
                        return JsonResponse({'response':'Some Exception occured.'})
            
            try:
                if not 'user_data' in request.session:
                    data=json.loads(request.body)
                    print(data)
                    prompt=data['message']
                    print(prompt)
                    messages=[{'role':'system','content':"You are trained so that you are personal assistant.Give answer whatever is asked.use proper emojis and other things etc. and do not use irrelevant chars or dashes.dont use stars or dashes"},
                            {'role':'user','content':prompt}]
                    client=OpenAI(api_key=config('API_KEY'))
                    responses=client.chat.completions.create(model='gpt-5.4-mini',
                                                messages=messages,
                                                temperature=0,
                                                n=1,
                                                stop=None,
                                                )

                    response=responses.choices[0].message.content
                    json_result={"label":response}
                    user_data={1:f'{prompt}_{response}'}
                    request.session['user_data']=user_data
                    last=request.session.get("user_data")
                    print(f'without session:{last}')
                    return JsonResponse({'response':response})

            except Exception as e:
                    print(e)
                    error={'label':'some exception occured.'}
                    print("some exception occure right here")
                    return JsonResponse({'response':'Some Exception occured.'})
            
    
    if request.user.is_authenticated:
        if request.method == 'POST':
            try:
                data=json.loads(request.body)
                prompt=data['message']
                chat_id=data['chat_id']
                chat=Chat.objects.filter(id=chat_id).first()
                messages=[{'role':'system','content':"You are trained so that you are personal assistant.Give answer whatever is asked.use proper emojis and other things etc. and do not use irrelevant chars or dashes.do not use stars or dashes"}]
                chat=MessagesTable.objects.select_related('chat').filter(chat=chat).order_by('created_at')
                for chat in chat:
                    role=chat.role
                    content=chat.content
                    another_msg={'role':role,'content':content}
                    messages.append(another_msg)
                messages.append({'role':'user','content':prompt})
                print(messages)
                client=OpenAI(api_key=config('API_KEY'))
                responses=client.chat.completions.create(model='gpt-5.4-mini',
                                                    messages=messages,
                                                    temperature=0,
                                                    n=1,
                                                    stop=None,
                                                    )


                response=responses.choices[0].message.content
                chat=Chat.objects.filter(id=chat_id,user=request.user).first()
                MessagesTable.objects.create(chat=chat,role='user',content=prompt)
                MessagesTable.objects.create(chat=chat,role='system',content=response)
                return JsonResponse({'response':response})

            except Exception as e:
                print(e)
                return JsonResponse({'response':'Network Error.'})
    return render(request,'assistant_gpt/home.html')

def session_chat(request):
      try:
            chat=request.session.get('user_data')
            final_result=[]
            if chat:    
                for key,value in chat.items():
                    user,system=value.split("_")
                    chat_1={'role':'user','content':user}
                    final_result.append(chat_1)
                    chat_2={'role':'system','content':system}
                    final_result.append(chat_2)

            print(final_result)
                
            return JsonResponse({"messages":final_result})
      except:
        return JsonResponse({'response':'Some Exception occured.'})





def register(request):
      try:
        if request.method == 'POST':
            form=RegisterForm(request.POST)
            print(form.errors)
            if form.is_valid():
                password=form.cleaned_data['password']
                user=form.save(commit=False)
                user.set_password(password)
                user.save()

                id=user.id
                email=user.email
                uid=urlsafe_base64_encode(force_bytes(id))
                token=default_token_generator.make_token(user)
                url=reverse('activate_account',kwargs={'uid':uid,'token':token})
                redirect_url=f'{settings.SITE_URL}{url}'
                email_sender(redirect_url,email)
                messages.success(request,'Activation link has been sent to your email click on it to activate your account.')
                return redirect('home')
        else:  
            form=RegisterForm()
      except Exception as e:
            print(e)
            messages.error(request,'Some exception occured.Try again.')
            return redirect('home')
      return render(request,'assistant_gpt/register.html',{'form':form})

def activate_account(request,uid,token):
    try:
        id=force_str(urlsafe_base64_decode(uid))
        user=CustomUser.objects.filter(id=id).first()
        if not user:
            messages.error(request,'Invalid link.')
            return redirect('login')
        else:
            if default_token_generator.check_token(user,token):
                if user.is_active is True:
                    messages.debug(request,'This user has already been activated.')
                    return redirect('login')
                else:
                    user.is_active=True
                    user.save()
                    messages.success(request,'Your account has been successfully activated.')
                    return redirect('login')
                
            else:
                messages.error(request,'Invalid link or it has been expired.')
                return redirect('login')


    except:
        messages.error('Invalid link or it has been expired.')
        return redirect('login')

def loginview(request):
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        email=request.POST.get('email')
        password=request.POST.get('password')
        print(email)
        print(password)

        if not email or not password:
            messages.error(request,'Email is required.')
            return redirect('login')
        
        else:
            try:
                user=authenticate(request,email=email,password=password)
                print(user)
            except:
                messages.error(request,'Invalid email or passwrod.1')
                return redirect('login')
        
        if user:
            if user.is_active is not True:
                messages.error(request,'User is not Activated.')
                return redirect('login')
            
            if user is not None:
                login(request,user)
                return redirect('home')
            
            else:
                messages.error(request,'Invalid email or password.2')
                return redirect('login')
        
        else:
            messages.error(request,'Invalid email or password.0')
            return redirect('login')
              
            
    return render(request,'assistant_gpt/login.html')

@login_required
def create_chat(request):
    data=json.loads(request.body)
    title=data['title']
    title=title.strip()
    title=escape(title)
    if len(title) >= 50:
        return JsonResponse({'error':'Title must be less than 50 characters.'},status=400)
    chat=Chat.objects.create(user=request.user,title=title)
    response={'chat_id':chat.id}
    return JsonResponse(data=response)


def chats(request):
    if request.user.is_authenticated:
        user=request.user
        chats=Chat.objects.select_related('user').filter(user=user).values('id','title').order_by('-created_at')
       
        chats=list(chats)
        for c in chats:
            c['id']=str(c['id'])
        print(chats)
        data={"chats":chats}
        return JsonResponse(data)
    
    else:
        return JsonResponse({'status':'ok'})
        
def load_chat(request,chat_id):
    if request.user.is_authenticated:
        chat_id=uuid.UUID(chat_id)
        chat=Chat.objects.filter(id=chat_id).first()
        chat=MessagesTable.objects.select_related('chat').filter(chat=chat).values('role','content').order_by('created_at')
        chat=list(chat)
        print(chat)
        return JsonResponse({'messages':chat})
    
    return render(request,'assistant_gpt/home.html',{'active_chat_id':chat_id})

@ensure_csrf_cookie
def url_chat(request,chat_id=None):
    return render(request,'assistant_gpt/home.html')

