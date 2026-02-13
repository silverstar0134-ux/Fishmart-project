from django import forms
from .models import AboutMessage


class ContactForm(forms.ModelForm):
    class Meta:
        model = AboutMessage
        fields = ['name', 'email', 'message']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Your Name',
                'required': True
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'Your Email',
                'required': True
            }),
            'message': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Your Message',
                'rows': 5,
                'required': True
            })
        }


class AdminReplyForm(forms.ModelForm):
    class Meta:
        model = AboutMessage
        fields = ['reply']
        widgets = {
            'reply': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Admin Reply',
                'rows': 5,
                'required': True
            })
        }
