from django import forms

class NewFilterForm(forms.Form):
    system_name = forms.SlugField(max_length = 50)

class FilterTestForm(forms.Form):
    test_obj = forms.CharField()

class FilterTestUserForm(forms.Form):
    user = forms.CharField()

class EditFilterForm(forms.Form):
    name = forms.CharField(max_length=255)
    value = forms.CharField(max_length=255)
