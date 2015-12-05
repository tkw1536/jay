from django import forms

class EditVoteForm(forms.Form):
    name = forms.CharField(max_length = 64)
    machine_name = forms.SlugField(max_length = 64)
    description = forms.CharField()

class EditVoteFilterForm(forms.Form):
    filter_id = forms.IntegerField()

class EditVoteOptionsForm(forms.Form):
    min_votes = forms.IntegerField()
    max_votes = forms.IntegerField()

class GetVoteOptionForm(forms.Form):
    option_id = forms.IntegerField()

class EditVoteOptionForm(forms.Form):
    option_id = forms.IntegerField()

    name = forms.CharField(required = False, max_length = 64)
    description = forms.CharField(required = False)
    personal_link = forms.URLField(required = False)
    link_name = forms.CharField(required = False, max_length = 16)