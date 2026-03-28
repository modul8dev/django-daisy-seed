from django import forms


class AccountSelectionForm(forms.Form):
    account_id = forms.CharField(widget=forms.HiddenInput)
