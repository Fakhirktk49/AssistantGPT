from django import forms
from core.models import CustomUser
from django.core.validators import RegexValidator
from core.models import CustomUser



password_regex = RegexValidator(
    regex=r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$',
    message='Password must contain at least one lowercase letter, one uppercase letter, one digit, one special character, and be at least 8 characters long.'
)
class RegisterForm(forms.ModelForm):
    password=forms.CharField(label="Password",validators=[],widget=forms.PasswordInput(attrs={'class':"w-full mt-1 p-3 rounded-xl bg-[#2a2a2a] text-white outline-none focus:ring-2 focus:ring-green-500",'placeholder':'Please a strong password.'}))
    conf_password=forms.CharField(label="Confirm Password",widget=forms.PasswordInput(attrs={'class':"w-full mt-1 p-3 rounded-xl bg-[#2a2a2a] text-white outline-none focus:ring-2 focus:ring-green-500"}))
    class Meta:
        model=CustomUser

        fields=['email']

        widgets={
            'email':forms.EmailInput(attrs={'class':"w-full mt-1 p-3 rounded-xl bg-[#2a2a2a] text-white outline-none focus:ring-2 focus:ring-green-500"})
        }

        
    def clean_email(self):
        email=self.cleaned_data.get('email')
        
        if CustomUser.objects.filter(email=email).exists():
            raise ValueError("This Email has already been registered.")
        
        return email
    
