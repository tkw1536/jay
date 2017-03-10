import json

from django.shortcuts import render

from votes.models import Vote, Status
from filters.models import UserFilter
from users.models import UserProfile

# Create your views here.
def home(request):
    ctx = {}
    votes = Vote.objects.filter(status__stage=Status.OPEN)
    results = Vote.objects.filter(status__stage=Status.PUBLIC)

    if request.user.is_authenticated():
        try:
            details = request.user.socialaccount_set.get(
                provider='dreamjub').extra_data
        except request.user.DoesNotExist:
            details = {}

        votes_shown = [v for v in votes if v.filter.matches(json.loads(
            details))]

        ctx["vote_list_title"] = "Your votes"

        if len(votes) != len(votes_shown):
            ctx["eligible_alert"] = True
    else:
        votes_shown = votes

    ctx["votes"] = votes_shown
    ctx["results"] = results

    return render(request, "home.html", ctx)
