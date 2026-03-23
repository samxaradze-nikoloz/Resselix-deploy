
from django import forms
from django.forms import modelformset_factory
from .models import Post, PostImage

class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['title', 'content', 'price', 'address', 'latitude', 'longitude']
        widgets = {
            'latitude': forms.HiddenInput(),
            'longitude': forms.HiddenInput(),
            'address': forms.TextInput(attrs={'id': 'pac-input', 'placeholder': 'Search for a location'}),
        }


PostImageFormSet = modelformset_factory(
    PostImage,
    fields=('image',),
    extra=3,  # how many upload fields you want
    widgets={'image': forms.ClearableFileInput()}
)