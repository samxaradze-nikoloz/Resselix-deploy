from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import Profile

class UserRegisterForm(UserCreationForm):
    email = forms.EmailField()

    class Meta:
        model = User
        fields = ['username', 'email'] # UserCreationForm handles passwords automatically

class UserUpdateForm(forms.ModelForm):
    email = forms.EmailField()

    class Meta:
        model = User
        fields = ['username', 'email']

class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = Profile
        # CRITICAL: Added address, latitude, and longitude here
        fields = ['image', 'phone_number', 'address', 'latitude', 'longitude']
        
        widgets = {
            'phone_number': forms.TextInput(attrs={
                'class': 'form-control', 
                'id': 'id_phone_number',
                'placeholder': 'Enter mobile number'
            }),
            'address': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g. 123 Street, Tbilisi'
            }),
            # We keep these as text inputs so the JavaScript can fill them
            'latitude': forms.TextInput(attrs={'readonly': 'readonly'}),
            'longitude': forms.TextInput(attrs={'readonly': 'readonly'}),
        }