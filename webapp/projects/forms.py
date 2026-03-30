from django import forms

from .models import Project


class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ['name']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'input input-bordered w-full',
                'placeholder': 'Project name',
            }),
        }


class ProjectSettingsForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ['enable_linkedin', 'enable_x', 'enable_facebook', 'enable_instagram']
        widgets = {
            'enable_linkedin': forms.CheckboxInput(attrs={'class': 'checkbox checkbox-primary'}),
            'enable_x': forms.CheckboxInput(attrs={'class': 'checkbox checkbox-primary'}),
            'enable_facebook': forms.CheckboxInput(attrs={'class': 'checkbox checkbox-primary'}),
            'enable_instagram': forms.CheckboxInput(attrs={'class': 'checkbox checkbox-primary'}),
        }
