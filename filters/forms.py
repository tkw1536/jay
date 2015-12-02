from django import forms

class NewFilterForm(forms.Form):
    machine_name = forms.SlugField(max_length = 50)