import json

from django.shortcuts import render, get_object_or_404, render_to_response

from django.http import HttpResponse
from django.views.generic import View

from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator

from votes.models import Vote
from filters.models import UserFilter
from users.models import UserProfile

# TODO Check eligibility on GET already

class VoteView(View):
    @method_decorator(login_required)
    def get(self, request, system_name, vote_name):
        vote = get_object_or_404(Vote, machine_name=vote_name)
        filter = vote.filter

        error = False

        ctx = {}
        ctx['vote'] = vote

        options = vote.option_set.all()
        ctx['options'] = options

        try:
            user_details = json.loads(request.user.profile.details)

            if not filter:
                ctx['alert_head'] = "No filter given."
                ctx['alert_text'] = "This vote has not been configured properly."
                error = True
            elif not filter.matches(user_details):
                ctx['alert_head'] = "Not eligible"
                ctx['alert_text'] = "You are not eligible for this vote. Tough luck."
                error = True

        except UserProfile.DoesNotExist:
            ctx['alert_head'] = "User details invalid."
            ctx['alert_text'] = "Your user details could not be retrieved from CampusNet. Please log out and try again later."
            error = True

        if not error:
            return render_to_response("vote/vote_vote.html", context=ctx)
        else:
            return render_to_response("vote/vote_error.html", context=ctx)

    def post(self, request):
        return HttpResponse("TODO: Write vote processing code")
