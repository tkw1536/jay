from django.shortcuts import render, get_object_or_404, render_to_response

from votes.models import Vote

# Create your views here.
def vote(request, vote_name):
    vote = get_object_or_404(Vote, machine_name=vote_name)
    options = vote.option_set.all()

    ctx = {}

    ctx['vote'] = vote
    ctx['options'] = options

    return render_to_response("vote/vote_vote.html", context=ctx)
