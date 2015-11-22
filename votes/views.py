import json

from django.shortcuts import render, get_object_or_404, render_to_response

from django.http import HttpResponse
from django.views.generic import View

from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator

from votes.models import Vote
from filters.models import UserFilter

# TODO Check eligibility on GET already

class VoteView(View):
    @method_decorator(login_required)
    def get(self, request, system_name, vote_name):
        vote = get_object_or_404(Vote, machine_name=vote_name)
        filter = vote.filter

        user_details = json.loads(request.user.profile.details)

        if not user_details:
            return HttpResponse("User details invalid. Try logging in again.")

        if not filter:
            return HttpResponse("No filter given. Admin, fix it.")

        print(user_details)

        if not filter.matches(user_details):
            print("User doesn't match filter.")
            return HttpResponse("You are not eligible")

        options = vote.option_set.all()

        ctx = {}

        ctx['vote'] = vote
        ctx['options'] = options

        return render_to_response("vote/vote_vote.html", context=ctx)

    def post(self, request):
        return HttpResponse("TODO: Write vote processing code")
