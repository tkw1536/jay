import json

from django.shortcuts import render

from votes.models import Vote
from filters.models import UserFilter
from users.models import UserProfile

# Create your views here.
def home(request):
    ctx = {}
    votes = Vote.objects.all()

    if request.user.is_authenticated():
        details = json.loads(request.user.profile.details)
        votes = filter(lambda x: x.filter.matches(details), votes)
        ctx["vote_list_title"] = "Your votes"

    ctx["votes"] = votes

    return render(request, "home.html", ctx)
