import json

from django.shortcuts import render, get_object_or_404, render_to_response

from django.http import HttpResponse
from django.views.generic import View

from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator

from votes.models import Vote, Option, Status, ActiveVote
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

        # TODO Check status of vote

        try:
            user_details = json.loads(request.user.profile.details)

            if not filter:
                ctx['alert_head'] = "No filter given."
                ctx['alert_text'] = "This vote has not been configured properly."
            elif not filter.matches(user_details):
                ctx['alert_head'] = "Not eligible"
                ctx['alert_text'] = "You are not eligible for this vote. Tough luck."

        except UserProfile.DoesNotExist:
            ctx['alert_head'] = "User details invalid."
            ctx['alert_text'] = "Your user details could not be retrieved from CampusNet. Please log out and try again later."

        if 'alert_head' in ctx:
            error = True

        if not error:
            return render(request, "vote/vote_vote.html", context=ctx)
        else:
            return render(request, "vote/vote_error.html", context=ctx, status=403)

    def render_error_response(self, ctx):
        return render_to_response("vote/vote_error.html", context=ctx)

    @method_decorator(login_required)
    def post(self, request, system_name, vote_name):
        ctx = {}

        # Make sure all the POST params are present
        if not 'vote_id' in request.POST:
            ctx['alert_head'] = "Something happened."
            ctx['alert_text'] = "Go back to the start and try again."
            return render_error_response(ctx)

        if not 'options_selected' in request.POST:
            ctx['alert_head'] = "Something happened."
            ctx['alert_text'] = "Go back and start over."
            return render_error_response(ctx)


        options = json.loads(request.POST['options_selected'])

        vote = get_object_or_404(Vote, machine_name=vote_name)
        filter = vote.filter

        error = False

        options_obj = Option.objects.filter(id__in=options, vote__id=vote.id)

        ctx['vote'] = vote
        ctx['options'] = options_obj

        if not (len(options_obj) >= vote.min_votes and len(options_obj) <= vote.max_votes):
            ctx['alert_head'] = "Invalid selection."
            ctx['alert_text'] = "Invalid number of options selected."
            return self.render_error_response(ctx)

        try:
            user_details = json.loads(request.user.profile.details)

            if not filter:
                ctx['alert_head'] = "No filter given."
                ctx['alert_text'] = "This vote has not been configured properly."
            elif not filter.matches(user_details):
                ctx['alert_head'] = "Not eligible"
                ctx['alert_text'] = "You are not eligible for this vote. Tough luck."

        except UserProfile.DoesNotExist:
            ctx['alert_head'] = "User details invalid."
            ctx['alert_text'] = "Your user details could not be retrieved from CampusNet. Please log out and try again later."

        if 'alert_head' in ctx:
            return self.render_error_response(ctx)

        # TODO Check status of vote before counting vote
        # TODO Do the actual vote counting

        return HttpResponse("It worked, but did nothing. TODO Put something more affirmative here.")
