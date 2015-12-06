import json

from django.shortcuts import render, get_object_or_404, render_to_response, redirect

from django.db import transaction
from django.db.models import F

from django.http import HttpResponse, Http404

from django.views.generic import View

from django.core.exceptions import PermissionDenied
from django.core.urlresolvers import reverse

from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator

from votes.models import Vote, Option, Status, ActiveVote
from filters.models import UserFilter
from users.models import UserProfile
from settings.models import VotingSystem

from votes.forms import EditVoteForm, EditVoteFilterForm, EditVoteOptionsForm, GetVoteOptionForm, EditVoteOptionForm

VOTE_ERROR_TEMPLATE = "vote/vote_msg.html"
VOTE_RESULT_TEMPLATE = "vote/vote_result.html"
VOTE_EDIT_TEMPLATE = "vote/vote_edit.html"

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

@login_required
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

@login_required
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

@login_required
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


def vote_edit_context(request, system_name, vote_name):
    """
        Returns context and basic parameters for vote editing.
    """
    (system, vote) = get_vote_and_system_or_404(system_name, vote_name)

    # raise an error if the user trying to access is not an admin
    if not system.isAdmin(request.user.profile):
        raise PermissionDenied

    # make a context
    ctx = {}

    # get all the systems this user can edit
    (admin_systems, other_systems) = request.user.profile.getSystems()

    # add the vote to the system
    ctx['vote'] = vote
    ctx['vote_options'] = vote.option_set.order_by("number")

    ctx['vote_uri'] = request.build_absolute_uri(
        reverse('votes:vote', kwargs={
            "system_name": system.machine_name,
            "vote_name":vote.machine_name
        })
    )
    ctx['results_uri'] = request.build_absolute_uri(
        reverse('votes:results', kwargs={
            "system_name": system.machine_name,
            "vote_name":vote.machine_name
        })
    )

    # and the filters
    ctx['admin_systems'] = admin_systems
    ctx['other_systems'] = other_systems

    # check if the vote is read only
    ctx["vote_readonly"] = not vote.canBeModified()

    return (system, vote, ctx)

@login_required
def vote_edit(request, system_name, vote_name):
    (system, vote, ctx) = vote_edit_context(request, system_name, vote_name)

    if request.method == "POST":

        # if the vote is read-only, do not save
        if ctx["vote_readonly"]:
            ctx['alert_head'] = 'Saving failed'
            ctx['alert_text'] = 'Nice try. A vote that has been opened can not be edited. '
            return render(request, VOTE_EDIT_TEMPLATE, ctx)

        # try to parse the form
        try:
            form = EditVoteForm(request.POST)

            if not form.is_valid():
                raise Exception
        except:
            ctx['alert_head'] = 'Saving failed'
            ctx['alert_text'] = 'Invalid data submitted'
            return render(request, VOTE_EDIT_TEMPLATE, ctx)

        # write the name and value, then save it in the database
        try:
            # store the name and value
            vote.name = form.cleaned_data['name']
            vote.machine_name = form.cleaned_data['machine_name']
            vote.description = form.cleaned_data['description']

            # and try to clean + save
            vote.clean()
            vote.save()
        except Exception as e:
            vote.machine_name = vote_name
            ctx['alert_head'] = 'Saving failed'
            ctx['alert_text'] = str(e)
            return render(request, VOTE_EDIT_TEMPLATE, ctx)

        # we did it, we saved
        ctx['alert_type'] = 'success'
        ctx['alert_head'] = 'Saving suceeded'
        ctx['alert_text'] = 'Form saved'

    # render the template
    return render(request, VOTE_EDIT_TEMPLATE, ctx)

@login_required
def vote_filter(request, system_name, vote_name):
    # you may only use POST
    if request.method != "POST":
        raise Http404

    (system, vote, ctx) = vote_edit_context(request, system_name, vote_name)

    # if the vote is read-only, do not save
    if ctx["vote_readonly"]:
        ctx['alert_head'] = 'Saving failed'
        ctx['alert_text'] = 'Nice try. A vote that has been opened can not be edited. '
        return render(request, VOTE_EDIT_TEMPLATE, ctx)

    # now try and parse the form
    try:
        form = EditVoteFilterForm(request.POST)

        if not form.is_valid():
            raise Exception
    except:
        ctx['alert_head'] = 'Saving failed'
        ctx['alert_text'] = 'Invalid data submitted'
        return render(request, VOTE_EDIT_TEMPLATE, ctx)

    # write filter, then save to db.
    try:
        # store the filter by id
        vote.filter = UserFilter.objects.filter(id=form.cleaned_data["filter_id"])[0]

        # and try to clean + save
        vote.clean()
        vote.save()
    except Exception as e:
        vote.machine_name = vote_name
        ctx['alert_head'] = 'Saving filter failed'
        ctx['alert_text'] = str(e)
        return render(request, VOTE_EDIT_TEMPLATE, ctx)

    # Woo, we made it
    ctx['alert_type'] = 'success'
    ctx['alert_head'] = 'Saving suceeded'
    ctx['alert_text'] = 'Associated filter has been updated. '

    # so render the basic template
    return render(request, VOTE_EDIT_TEMPLATE, ctx)

@login_required
def vote_option(request, system_name, vote_name):
    # you may only use POST
    if request.method != "POST":
        raise Http404

    (system, vote, ctx) = vote_edit_context(request, system_name, vote_name)

    # if the vote is read-only, do not save
    if ctx["vote_readonly"]:
        ctx['alert_head'] = 'Saving failed'
        ctx['alert_text'] = 'Nice try. A vote that has been opened can not be edited. '
        return render(request, VOTE_EDIT_TEMPLATE, ctx)

    # now try and parse the form
    try:
        form = EditVoteOptionsForm(request.POST)

        if not form.is_valid():
            raise Exception
    except:

        ctx['alert_head'] = 'Saving failed'
        ctx['alert_text'] = 'Invalid data submitted'
        return render(request, VOTE_EDIT_TEMPLATE, ctx)

    min_votes = form.cleaned_data["min_votes"]
    max_votes = form.cleaned_data["max_votes"]
    count = vote.option_set.count()

    # read min and max votes, then store them
    try:

        # check range for min votes
        if min_votes < 0 or min_votes > count:
            raise Exception("Minimum number of votes must be between 0 and the number of available options. ")

        # check range for max votes
        if max_votes < 0 or max_votes > count:
            raise Exception("Maximum number of votes must be between 0 and the number of available options. ")

        if min_votes > max_votes:
            raise Exception("The maximum number of votes may not be smaller than the minimum number of votes. ")


        vote.min_votes = min_votes
        vote.max_votes = max_votes

        # and try to clean + save
        vote.clean()
        vote.save()
    except Exception as e:
        vote.machine_name = vote_name
        ctx['alert_head'] = 'Saving vote failed'
        ctx['alert_text'] = str(e)
        return render(request, VOTE_EDIT_TEMPLATE, ctx)

    # Woo, we made it
    ctx['alert_type'] = 'success'
    ctx['alert_head'] = 'Saving suceeded'
    ctx['alert_text'] = 'Number of vote options updated. '

    # so render the basic template
    return render(request, VOTE_EDIT_TEMPLATE, ctx)


@login_required
def vote_options_add(request, system_name, vote_name):
    # you may only use POST
    if request.method != "POST":
        raise Http404

    (system, vote, ctx) = vote_edit_context(request, system_name, vote_name)

    # if the vote is read-only, do not save
    if ctx["vote_readonly"]:
        ctx['alert_head'] = 'Saving failed'
        ctx['alert_text'] = 'Nice try. A vote that has been opened can not be edited. '
        return render(request, VOTE_EDIT_TEMPLATE, ctx)

    # try to add an option
    try:
        vote.addOption()
    except Exception as e:
        ctx['alert_head'] = 'Adding option failed'
        ctx['alert_text'] = 'Something went wrong. '
        return render(request, VOTE_EDIT_TEMPLATE, ctx)

    # and done
    ctx['alert_type'] = 'success'
    ctx['alert_head'] = 'Adding option suceeded'
    ctx['alert_text'] = 'New option added. '
    return render(request, VOTE_EDIT_TEMPLATE, ctx)

@login_required
def vote_options_edit(request, system_name, vote_name):
    # you may only use POST
    if request.method != "POST":
        raise Http404

    (system, vote, ctx) = vote_edit_context(request, system_name, vote_name)

    # if the vote is read-only, do not save
    if ctx["vote_readonly"]:
        ctx['alert_head'] = 'Saving failed'
        ctx['alert_text'] = 'Nice try. A vote that has been opened can not be edited. '
        return render(request, VOTE_EDIT_TEMPLATE, ctx)

    try:
        form = EditVoteOptionForm(request.POST)

        if not form.is_valid():
            raise Exception
    except Exception as e:
        ctx['alert_head'] = 'Saving failed'
        ctx['alert_text'] = 'Invalid data submitted'
        return render(request, VOTE_EDIT_TEMPLATE, ctx)

    # try to find the option
    try:
        option = Option.objects.filter(id=form.cleaned_data["option_id"])[0]

        if not option.id in vote.option_set.values_list('id', flat=True):
            raise Exception
    except:
        ctx['alert_head'] = 'Saving failed'
        ctx['alert_text'] = 'Nice try. That option does not exist. '
        return render(request, VOTE_EDIT_TEMPLATE, ctx)

    # try and store the values
    try:
        option.name = form.cleaned_data["name"]
        option.description = form.cleaned_data["description"]
        option.personal_link = form.cleaned_data["personal_link"]
        option.link_name = form.cleaned_data["link_name"]

        option.clean()
        option.save()
    except Exception as e:
        ctx['alert_head'] = 'Saving option failed'
        ctx['alert_text'] = str(e)
        return render(request, VOTE_EDIT_TEMPLATE, ctx)

    # Woo, we made it
    ctx['alert_type'] = 'success'
    ctx['alert_head'] = 'Saving suceeded'
    ctx['alert_text'] = 'Option saved'

    # so render the basic template
    return render(request, VOTE_EDIT_TEMPLATE, ctx)

@login_required
def vote_options_remove(request, system_name, vote_name):
    # you may only use POST
    if request.method != "POST":
        raise Http404

    (system, vote, ctx) = vote_edit_context(request, system_name, vote_name)

    # if the vote is read-only, do not save
    if ctx["vote_readonly"]:
        ctx['alert_head'] = 'Saving failed'
        ctx['alert_text'] = 'Nice try. A vote that has been opened can not be edited. '
        return render(request, VOTE_EDIT_TEMPLATE, ctx)

    try:
        form = GetVoteOptionForm(request.POST)

        if not form.is_valid():
            raise Exception
    except:
        ctx['alert_head'] = 'Saving failed'
        ctx['alert_text'] = 'Invalid data submitted'
        return render(request, VOTE_EDIT_TEMPLATE, ctx)

    try:
        # find the option
        option = Option.objects.filter(id=form.cleaned_data["option_id"])[0]
    except:
        ctx['alert_head'] = 'Saving failed'
        ctx['alert_text'] = 'Nice try. That option does not exist. '
        return render(request, VOTE_EDIT_TEMPLATE, ctx)

    # and try to remove it
    try:
        vote.deleteOption(option)
    except Exception as e:
        ctx['alert_head'] = 'Saving failed'
        ctx['alert_text'] = str(e)
        return render(request, VOTE_EDIT_TEMPLATE, ctx)

    # and done
    ctx['alert_type'] = 'success'
    ctx['alert_head'] = 'Options updated'
    ctx['alert_text'] = 'Option removed. '
    return render(request, VOTE_EDIT_TEMPLATE, ctx)

@login_required
def vote_options_down(request, system_name, vote_name):
    # you may only use POST
    if request.method != "POST":
        raise Http404

    (system, vote, ctx) = vote_edit_context(request, system_name, vote_name)

    # if the vote is read-only, do not save
    if ctx["vote_readonly"]:
        ctx['alert_head'] = 'Saving failed'
        ctx['alert_text'] = 'Nice try. A vote that has been opened can not be edited. '
        return render(request, VOTE_EDIT_TEMPLATE, ctx)

    try:
        form = GetVoteOptionForm(request.POST)

        if not form.is_valid():
            raise Exception
    except:
        ctx['alert_head'] = 'Saving failed'
        ctx['alert_text'] = 'Invalid data submitted'
        return render(request, VOTE_EDIT_TEMPLATE, ctx)

    try:
        # find the option
        option = Option.objects.filter(id=form.cleaned_data["option_id"])[0]
    except:
        ctx['alert_head'] = 'Saving failed'
        ctx['alert_text'] = 'Nice try. That option does not exist. '
        return render(request, VOTE_EDIT_TEMPLATE, ctx)

    # and try to remove it
    try:
        vote.moveUpOption(option)
    except Exception as e:
        ctx['alert_head'] = 'Saving failed'
        ctx['alert_text'] = str(e)
        return render(request, VOTE_EDIT_TEMPLATE, ctx)

    # and done
    ctx['alert_type'] = 'success'
    ctx['alert_head'] = 'Options updated'
    ctx['alert_text'] = 'Option moved down. '
    return render(request, VOTE_EDIT_TEMPLATE, ctx)

@login_required
def vote_options_up(request, system_name, vote_name):
    # you may only use POST
    if request.method != "POST":
        raise Http404

    (system, vote, ctx) = vote_edit_context(request, system_name, vote_name)

    # if the vote is read-only, do not save
    if ctx["vote_readonly"]:
        ctx['alert_head'] = 'Saving failed'
        ctx['alert_text'] = 'Nice try. A vote that has been opened can not be edited. '
        return render(request, VOTE_EDIT_TEMPLATE, ctx)

    try:
        form = GetVoteOptionForm(request.POST)

        if not form.is_valid():
            raise Exception
    except:
        ctx['alert_head'] = 'Saving failed'
        ctx['alert_text'] = 'Invalid data submitted'
        return render(request, VOTE_EDIT_TEMPLATE, ctx)

    try:
        # find the option
        option = Option.objects.filter(id=form.cleaned_data["option_id"])[0]
    except:
        ctx['alert_head'] = 'Saving failed'
        ctx['alert_text'] = 'Nice try. That option does not exist. '
        return render(request, VOTE_EDIT_TEMPLATE, ctx)

    # and try to remove it
    try:
        vote.moveDownOption(option)
    except Exception as e:
        ctx['alert_head'] = 'Saving failed'
        ctx['alert_text'] = str(e)
        return render(request, VOTE_EDIT_TEMPLATE, ctx)

    # and done
    ctx['alert_type'] = 'success'
    ctx['alert_head'] = 'Options updated'
    ctx['alert_text'] = 'Option moved up. '
    return render(request, VOTE_EDIT_TEMPLATE, ctx)



def results(request, system_name, vote_name):
    ctx = {}

    # grab vote and system
    (system, vote) = get_vote_and_system_or_404(system_name, vote_name)

    # set options and the vote
    ctx['vote'] = vote
    ctx['options'] = vote.option_set.order_by('-count')

    if vote.status.stage != Status.PUBLIC:
        ctx['alert_type'] = 'danger'
        ctx['alert_head'] = 'Non-public'
        ctx['alert_text'] = 'The results are not public yet. Please come back later.'

        return render(request, VOTE_ERROR_TEMPLATE, ctx)

    # render the stuff
    return render(request, VOTE_RESULT_TEMPLATE, ctx)

class VoteView(View):
    @method_decorator(login_required)
    def get(self, request, system_name, vote_name):
        (system, vote) = get_vote_and_system_or_404(system_name, vote_name)
        filter = vote.filter
        status = vote.status

        error = False

        ctx = {}
        ctx['vote'] = vote

        options = vote.option_set.order_by("number")
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

        if status.stage not in [Status.OPEN, Status.PUBLIC]:
            error = True

            ctx['alert_type'] = "danger"
            ctx['alert_head'] = "Not open"
            ctx['alert_text'] = "This vote is not open. Come back later."

        if not error:
            if status.stage == Status.PUBLIC:
                return redirect('votes:results', system_name=system.machine_name, vote_name=vote.machine_name)

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
