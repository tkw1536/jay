import json
from django.shortcuts import render, get_object_or_404, render_to_response
from django.db import transaction
from django.db.models import F
from django.http import HttpResponse
from django.views.generic import View
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator

from votes.models import Vote, Option, Status, ActiveVote
from filters.models import UserFilter
from users.models import UserProfile
from .models import VotingSystem

# Create your views here.
def overview(request):
	voting_system_list = VotingSystem.objects.all()
	context = {'voting_system_list': voting_system_list}
	return render(request, 'vs/voting_system_overview.html', context)
