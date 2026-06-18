from django.shortcuts import render
import json
from openai import OpenAI
from django.http import JsonResponse

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
     return render(request,'assistant_gpt/register.html')

