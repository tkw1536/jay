from django import forms

class EditSystemForm(forms.Form):
    machine_name = forms.SlugField(max_length = 50)
    simple_name = forms.CharField(max_length = 80)

class AddSuperAdminForm(forms.Form):
	user_id = forms.CharField(max_length = 80)
