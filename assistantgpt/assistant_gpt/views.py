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


# Create your views here.
def home(request):
    if request.method == 'POST':
        try:
            if 'user_data' in request.session:
                data=json.loads(request.body)
                prompt=data['text']
                user_data=request.session.get('user_data')
                messages=[{'role':'system','content':"You are trained so that you are personal assistant.Give answer whatever is asked."}]
                for key,values in user_data.items():
                    question,response=values.split('_')
                    messages.append({'role':'user','content':question})
                    messages.append({'role':'assistant','content':response})

                messages.append({'role':'user','content':f'prompt is in between "@3$32$#" give answer to it with in limit of 70 tokens.:@3$32$#{prompt}@3$32$#'})
                print(messages)         
                client=OpenAI(api_key="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")
                responses=client.chat.completions.create(model='gpt-4.1-mini',
                                            messages=messages,
                                            temperature=0,
                                            n=1,
                                            max_tokens=70,
                                            stop=None,
                                            )

                response=responses.choices[0].message.content
                json_result={"label":response}
                user_data=request.session.get('user_data')
                id=list(user_data.keys())[-1]
                id=int(id)
                id +=1
                user_data[id]=f'{prompt}_{response}'
                request.session['user_data']=user_data
                updated_session=request.session.get('user_data')
                print(updated_session)
                return JsonResponse(json_result,safe=False)
        except Exception as e:
                    print(e)
                    error={'label':'when session some exception occured.'}
                    return JsonResponse(error,safe=False)
        
        try:
            if not 'user_data' in request.session:
                data=json.loads(request.body)
                prompt=data['text']
                messages=[{'role':'system','content':"You are trained so that you are personal assistant.Give answer whatever is asked."},
                        {'role':'user','content':prompt}]
                client=OpenAI(api_key="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")
                responses=client.chat.completions.create(model='gpt-4.1-mini',
                                            messages=messages,
                                            temperature=0,
                                            n=1,
                                            max_tokens=70,
                                            stop=None,
                                            )

                response=responses.choices[0].message.content
                json_result={"label":response}
                user_data={1:f'{prompt}_{response}'}
                request.session['user_data']=user_data
                last=request.session.get("user_data")
                print(f'without session:{last}')
                return JsonResponse(json_result,safe=False)

        except Exception as e:
                print(e)
                error={'label':'some exception occured.'}
                return JsonResponse(error,safe=False)

    return render(request,'assistant_gpt/home.html')

def login(request):
     return render(request,'assistant_gpt/login.html')

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
            #    url=reverse('activate_account',kwargs={'uid':uid,'token':token})
            #     redirect_url=f'{settings.SITE_URL}{url}'
            #     email_sender(redirect_url,email)
                messages.success(request,'Activation link has been sent to your email click on it to activate your account.')
                return redirect('home')
        else:  
            form=RegisterForm()
      except Exception as e:
            print(e)
            messages.error(request,'Some exception occured.Try again.')
            return redirect('home')
      return render(request,'assistant_gpt/register.html',{'form':form})

