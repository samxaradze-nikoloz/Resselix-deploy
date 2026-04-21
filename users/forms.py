from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import Profile, Review

class UserRegisterForm(UserCreationForm):
    email = forms.EmailField()

    class Meta:
        model = User
        fields = ['username', 'email'] 

class UserUpdateForm(forms.ModelForm):
    email = forms.EmailField()

    class Meta:
        model = User
        fields = ['username', 'email']

class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = Profile

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

            'latitude': forms.TextInput(attrs={'readonly': 'readonly'}),
            'longitude': forms.TextInput(attrs={'readonly': 'readonly'}),
        }

class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['rating', 'content']
        widgets = {
            'rating': forms.RadioSelect(choices=[(i, i) for i in range(1, 6)]),
            'content': forms.Textarea(attrs={'rows': 3, 'class': 'form-control', 'placeholder': 'Describe your experience...'}),
        }