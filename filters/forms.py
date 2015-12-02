from django import forms

class NewFilterForm(forms.Form):
    system_name = forms.SlugField(max_length = 50)

class EditFilterForm(forms.Form):
    name = forms.CharField(max_length=255)
    value = forms.CharField(max_length=255)