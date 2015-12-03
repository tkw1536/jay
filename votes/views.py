import json

from django.shortcuts import render, get_object_or_404, render_to_response

from django.db import transaction
from django.db.models import F

from django.http import HttpResponse, Http404

from django.views.generic import View

from django.core.exceptions import PermissionDenied,

from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator

from votes.models import Vote, Option, Status, ActiveVote
from filters.models import UserFilter
from users.models import UserProfile
from settings.models import VotingSystem

VOTE_ERROR_TEMPLATE = "vote/vote_msg.html"
VOTE_RESULT_TEMPLATE = "vote/vote_result.html"


def get_vote_and_system_or_404(system_name, vote_name):
    """
        Gets a voting system and the corresponding vote or returns a 404.
    """
    system = get_object_or_404(VotingSystem, machine_name=system_name)
    vote = get_object_or_404(Vote, machine_name=vote_name, system=system)

    return (system, vote)

def system_home(request, system_name):
    ctx = {}
    ctx['vs'] = get_object_or_404(VotingSystem, machine_name=system_name)

    ctx['votes'] = Vote.objects.filter(system=ctx['vs'], status__stage=Status.OPEN)

    ctx['results'] = Vote.objects.filter(system=ctx['vs'], status__stage=Status.PUBLIC)

    return render(request, "vote/vote_system_overview.html", ctx)

def system_settings(request, system_name):

    # get the voting system
    ctx = {}
    vs = get_object_or_404(VotingSystem, machine_name=system_name)

    # raise an error if the user trying to access is not an admin
    if not vs.isAdmin(request.user.profile):
        raise PermissionDenied

    # TODO: @leonhard implement generic overview page for settings
    # should have an add admin, remove admin, add vote, delete vote button
    pass

def admin_add(request, system_name):

    # you may only use POST
    if request.method != "POST":
        raise Http404

    # get the voting system
    ctx = {}
    vs = get_object_or_404(VotingSystem, machine_name=system_name)

    # raise an error if the user trying to access is not an admin
    if not vs.isAdmin(request.user.profile):
        raise PermissionDenied

    # TODO: @leonhard implement adding a an admin to a voting system
    pass

def admin_remove(request, system_name):

    # you may only use POST
    if request.method != "POST":
        raise Http404

    # get the voting system
    ctx = {}
    vs = get_object_or_404(VotingSystem, machine_name=system_name)

    # raise an error if the user trying to access is not an admin
    if not vs.isAdmin(request.user.profile):
        raise PermissionDenied

    # TODO: @leonhard implement removing an admin from a voting system
    pass

def vote_edit(request, system_name, vote_name):
    (system, vote) = get_vote_and_system_or_404(system_name, vote_name)

    # raise an error if the user trying to access is not an admin
    if not system.isAdmin(request.user.profile):
        raise PermissionDenied

    # TODO: @tom Implement vote edit page.
    pass

def vote_edit(request, system_name, vote_name):
    # you may only use POST
    if request.method != "POST":
        raise Http404

    (system, vote) = get_vote_and_system_or_404(system_name, vote_name)

    # raise an error if the user trying to access is not an admin
    if not system.isAdmin(request.user.profile):
        raise PermissionDenied

    # TODO: @tom Implement vote edit page.
    pass

def vote_options_add(request, system_name, vote_name):
    # you may only use POST
    if request.method != "POST":
        raise Http404

    (system, vote) = get_vote_and_system_or_404(system_name, vote_name)

    # raise an error if the user trying to access is not an admin
    if not system.isAdmin(request.user.profile):
        raise PermissionDenied

    # TODO: @tom Implement adding an option
    pass

def vote_options_edit(request, system_name, vote_name):
    # you may only use POST
    if request.method != "POST":
        raise Http404

    (system, vote) = get_vote_and_system_or_404(system_name, vote_name)

    # raise an error if the user trying to access is not an admin
    if not system.isAdmin(request.user.profile):
        raise PermissionDenied

    # TODO: @tom Implement editing an option
    pass

def vote_options_remove(request, system_name, vote_name):
    # you may only use POST
    if request.method != "POST":
        raise Http404

    (system, vote) = get_vote_and_system_or_404(system_name, vote_name)

    # raise an error if the user trying to access is not an admin
    if not system.isAdmin(request.user.profile):
        raise PermissionDenied

    # TODO: @tom Implement removing an option
    pass



def results(request, system_name, vote_name):
    ctx = {}

    # grab vote and system
    (system, vote) = get_vote_and_system_or_404(system_name, vote_name)

    # set options and the vote
    ctx['vote'] = vote
    ctx['options'] = vote.option_set.order_by('-count')

    # render the stuff
    return render(request, VOTE_RESULT_TEMPLATE, ctx)

class VoteView(View):
    @method_decorator(login_required)
    def get(self, request, system_name, vote_name):
        (system, vote) = get_vote_and_system_or_404(system_name, vote_name)
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
                error = True
            elif not filter.matches(user_details):
                ctx['alert_head'] = "Not eligible"
                ctx['alert_text'] = "You are not eligible for this vote. Tough luck."
                error = True


        except UserProfile.DoesNotExist:
            ctx['alert_head'] = "User details invalid."
            ctx['alert_text'] = "Your user details could not be retrieved from CampusNet. Please log out and try again later."
            error = True

        try:
            av = ActiveVote.objects.get(user=request.user, vote=vote)
            ctx['alert_type'] = "warning"
            ctx['alert_head'] = "You have already voted."
            ctx['alert_text'] = "Every user can only vote once. You have."

        except ActiveVote.DoesNotExist:
            pass

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
            return self.render_error_response(ctx)

        if not 'options_selected' in request.POST:
            ctx['alert_head'] = "Something happened."
            ctx['alert_text'] = "Go back and start over."
            return self.render_error_response(ctx)


        options = json.loads(request.POST['options_selected'])

        (system, vote) = get_vote_and_system_or_404(system_name, vote_name)
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
