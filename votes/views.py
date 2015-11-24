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

VOTE_ERROR_TEMPLATE = "vote/vote_msg.html"

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
            return render(request, VOTE_ERROR_TEMPLATE, context=ctx, status=403)

    def render_error_response(self, ctx):
        return render_to_response(VOTE_ERROR_TEMPLATE, context=ctx)

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

        # Steps (all in one transaction)
        # 1. Check if user has already voted
        # 2. Increase count of selected options
        # 3. Create ActiveVote with vote and user

        with transaction.atomic():
            try:
                av = ActiveVote.objects.get(user=request.user, vote=vote)
                ctx['alert_head'] = "You have already voted."
                ctx['alert_text'] = "Every user can only vote once. You have."
                return self.render_error_response(ctx)

            except ActiveVote.DoesNotExist:
                av = ActiveVote(user=request.user, vote=vote)
                av.save()

                for opt in options_obj:
                    opt.count = F('count') + 1
                    opt.save()

        ctx = {}

        ctx['page_title'] = "Vote Done"
        ctx['alert_type'] = "success"
        ctx['alert_head'] = "You voted!"
        ctx['alert_text'] = "Your votes have been counted."

        return render_to_response(VOTE_ERROR_TEMPLATE, context=ctx)
