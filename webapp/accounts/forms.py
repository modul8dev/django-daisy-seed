from django import forms
from django.contrib.auth import get_user_model

User = get_user_model()


class ProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'company_name']
        widgets = {
            'first_name': forms.TextInput(attrs={
                'class': 'input input-bordered w-full rounded-lg text-sm',
                'placeholder': 'First name',
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'input input-bordered w-full rounded-lg text-sm',
                'placeholder': 'Last name',
            }),
            'company_name': forms.TextInput(attrs={
                'class': 'input input-bordered w-full rounded-lg text-sm',
                'placeholder': 'Company name',
            }),
        }
