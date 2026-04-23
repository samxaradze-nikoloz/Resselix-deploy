from django import forms
from django.forms import modelformset_factory
from .models import Post, PostImage


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = [
            'title',
            'content',
            'price',
            'category',
            'subcategory',   
            'address',
            'latitude',
            'longitude'
        ]

        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'content': forms.Textarea(attrs={'class': 'form-control'}),
            'price': forms.NumberInput(attrs={'class': 'form-control'}),

            'category': forms.Select(attrs={
                'class': 'form-select'
            }),

            'latitude': forms.HiddenInput(),
            'longitude': forms.HiddenInput(),

            'address': forms.TextInput(attrs={
                'id': 'pac-input',
                'class': 'form-control',
                'placeholder': 'Search for a location'
            }),
        }


PostImageFormSet = modelformset_factory(
    PostImage,
    fields=('image',),
    extra=3,
    widgets={
        'image': forms.ClearableFileInput(attrs={
            'class': 'form-control'
        })
    }
)



from .models import PostComment, ForumComment


class PostCommentForm(forms.ModelForm):
    class Meta:
        model = PostComment
        fields = ['content']
        widgets = {
            'content': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Write a comment...'
            })
        }


class ForumCommentForm(forms.ModelForm):
    class Meta:
        model = ForumComment
        fields = ['content']
        widgets = {
            'content': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Write a reply...'
            })
        }