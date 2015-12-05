from django import forms

class EditVoteForm(forms.Form):
    name = forms.CharField(max_length = 64)
    machine_name = forms.SlugField(max_length = 64)
    description = forms.CharField()

class EditVoteFilterForm(forms.Form):
    filter_id = forms.IntegerField()