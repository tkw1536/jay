from django import forms

class EditSystemForm(forms.Form):
    machine_name = forms.SlugField(max_length = 50)
    simple_name = forms.CharField(max_length = 80)
