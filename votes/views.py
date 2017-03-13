import json
import time

from django.shortcuts import render, get_object_or_404, render_to_response, redirect

from django.utils import formats

from django.db import transaction
from django.db.models import F

from django.http import HttpResponse, Http404

from django.views.generic import View

from django.core.exceptions import PermissionDenied
from django.core.urlresolvers import reverse

from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator

from votes.models import Vote, Option, Status, ActiveVote, PassiveVote
from filters.models import UserFilter
from users.models import UserProfile, Admin
from settings.models import VotingSystem

from django.contrib.auth.models import User

from votes.forms import EditVoteForm, EditVoteFilterForm, EditVoteOptionsForm, GetVoteOptionForm, EditVoteOptionForm, PasswordForm, EditScheduleForm, AdminSelectForm

VOTE_ERROR_TEMPLATE = "vote/vote_msg.html"
VOTE_RESULT_TEMPLATE = "vote/vote_result.html"
VOTE_EDIT_TEMPLATE = "vote/vote_edit.html"
SYS_EDIT_TEMPLATE = "vote/user_list.html"


def get_vote_and_system_or_404(system_name, vote_name):
    """
        Gets a voting system and the corresponding vote or returns a 404.
    """
    system = get_object_or_404(VotingSystem, machine_name=system_name)
    vote = get_object_or_404(Vote, machine_name=vote_name, system=system)

    return (system, vote)


def system_home(request, system_name):
    ctx = {}
    ctx['vs'] = vs = get_object_or_404(VotingSystem, machine_name=system_name)

    all_votes = Vote.objects.filter(system=vs)

    if request.user.is_authenticated() and vs.isAdmin(request.user):
        ctx['votes'] = all_votes
        ctx['results'] = Vote.objects.filter(system=vs, status__stage__in=[Status.PUBLIC, Status.CLOSE])

        ctx['alert_type'] = 'info'
        ctx['alert_head'] = 'Non-public items shown'
        ctx['alert_text'] = 'Some items shown here may not be public.'

        ctx['is_vs_admin'] = True

    else:
        ctx['votes'] = Vote.objects.filter(system=ctx['vs'], status__stage=Status.OPEN)
        ctx['results'] = Vote.objects.filter(system=ctx['vs'], status__stage=Status.PUBLIC)

    return render(request, "vote/vote_system_overview.html", ctx)

@login_required
def admin(request, system_name, alert_type=None, alert_head=None, alert_text=None):

    # get the voting system
    ctx = {}
    vs = get_object_or_404(VotingSystem, machine_name=system_name)

    # raise an error if the user trying to access is not an admin
    if not vs.isAdmin(request.user.profile):
        raise PermissionDenied

    ctx['vs'] = vs

    # add an alert state if needed
    if alert_head or alert_text or alert_type:
        ctx['alert_type'] = alert_type
        ctx['alert_head'] = alert_head
        ctx['alert_text'] = alert_text

    # all the admins
    ctx['admins'] = vs.admin_set.all()
    admin_users = [a.user for a in ctx['admins']]

    ctx['not_admins'] = [ u for u in User.objects.all() if not u in admin_users ]

    return render(request, SYS_EDIT_TEMPLATE, ctx)



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

    try:
        # parse the form
        form = AdminSelectForm(request.POST)

        if not form.is_valid():
            raise Exception

        user = User.objects.filter(username=form.cleaned_data["username"])[0]
    except:
        return admin(request, system_name=system_name, alert_head='Grant Failed', alert_text='Invalid data submitted')

    try:
        sa = Admin(user=user, system=vs)
        sa.save()
    except Exception as e:
        return admin(request, system_name=system_name, alert_head='Grant Failed', alert_text=str(e))

    return admin(request, system_name=system_name, alert_type = "success", alert_head = "Grant succeeded", alert_text = "User added to admins. ")
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

    try:
        # parse the form
        form = AdminSelectForm(request.POST)

        if not form.is_valid():
            raise Exception

        user = User.objects.filter(username=form.cleaned_data["username"])[0]
    except:
        return admin(request, system_name=system_name, alert_head='Removing failed', alert_text='Invalid data submitted')

    try:
        the_admin = Admin.objects.filter(system=vs, user=user)[0]

        if the_admin.user.username == request.user.username:
            raise Exception("Don't torture yourself. ")

        the_admin.delete()
    except Exception as e:
        return admin(request, system_name=system_name, alert_head='Removing failed. ', alert_text=str(e))

    return admin(request, system_name=system_name, alert_type = "success", alert_head = "Removing succeeded", alert_text = "User is no longer an admin. ")


def get_vote_props(ctx, vote):
    # check if the vote is read only
    ctx["vote_readonly"] = not vote.canBeModified()

    # check if the vote is staged
    ctx["vote_is_init"] = (vote.status.stage == Status.INIT)
    ctx["vote_is_staged"] = (vote.status.stage == Status.STAGED)
    ctx["vote_is_open"] = (vote.status.stage == Status.OPEN)
    ctx["vote_is_closed"] = (vote.status.stage == Status.CLOSE)
    ctx["vote_is_public"] = (vote.status.stage == Status.PUBLIC)

    # check for all the times
    ctx["vote_has_open_time"] = (vote.status.open_time != None)
    ctx["vote_has_close_time"] = (vote.status.close_time != None)
    ctx["vote_has_public_time"] = (vote.status.public_time != None)

    if ctx["vote_has_open_time"]:
        ctx["vote_open_time"] = vote.status.open_time.strftime("%Y-%m-%d %H:%M:%S")

    if ctx["vote_has_close_time"]:
        ctx["vote_close_time"] = vote.status.close_time.strftime("%Y-%m-%d %H:%M:%S")

    if ctx["vote_has_public_time"]:
        ctx["vote_public_time"] = vote.status.public_time.strftime("%Y-%m-%d %H:%M:%S")


    # and what we can do
    ctx["can_set_stage"] = ctx["vote_is_init"]
    ctx["can_set_time"] = ctx["vote_is_init"]

    ctx["can_update_eligibile"] = ctx["vote_is_staged"] or ctx["vote_is_open"] or ctx["vote_is_closed"]
    ctx["can_set_open"] = ctx["vote_is_staged"] and (not ctx["vote_has_open_time"])
    ctx["can_set_close"] = ctx["vote_is_open"] and (not ctx["vote_has_close_time"])
    ctx["can_set_public"] = ctx["vote_is_closed"] and (not ctx["vote_has_public_time"])

    return ctx


def vote_edit_context(request, system_name, vote_name):
    from jay import utils
    """
        Returns context and basic parameters for vote editing.
    """
    (system, vote) = get_vote_and_system_or_404(system_name, vote_name)

    # touch the vote
    vote.touch()

    # raise an error if the user trying to access is not an admin
    if not system.isAdmin(request.user):
        raise PermissionDenied

    # make a context
    ctx = {}

    # get all the systems this user can edit
    (admin_systems, other_systems) = utils.get_all_systems(request.user)

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

    # reload the stages
    ctx = get_vote_props(ctx, vote)

    return (system, vote, ctx)

@login_required
def vote_add(request, system_name):
    """
        Add a blank vote and redirect to its edit page
    """
    vs = get_object_or_404(VotingSystem, machine_name=system_name)

    # raise an error if the user trying to access is not an admin
    if not vs.isAdmin(request.user):
        raise PermissionDenied

    v = Vote()

    s = Status()
    s.save()

    now = str(int(time.time()))

    v.name = "Untitled Vote 1"
    v.machine_name = "new_" + now

    v.system = vs
    v.status = s
    v.creator = request.user

    v.min_votes = 0
    v.max_votes = 0

    v.save()

    return redirect('votes:edit', system_name=system_name, vote_name=v.machine_name)

@login_required
def vote_delete(request, system_name, vote_name):
    (system, vote, ctx) = vote_edit_context(request, system_name, vote_name)

    if vote.canDelete(request.user.profile):
        vote.delete()

    return redirect('votes:system', system_name=system_name)

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
def vote_stage(request, system_name, vote_name):
    # you may only use POST
    if request.method != "POST":
        raise Http404

    (system, vote, ctx) = vote_edit_context(request, system_name, vote_name)

    # if the vote is not closed, dont make it public
    if not ctx["can_set_stage"]:
        ctx['alert_head'] = 'Saving failed'
        ctx['alert_text'] = 'A vote can only be staged when it is in init stage. '
        return render(request, VOTE_EDIT_TEMPLATE, ctx)

    # now try and parse the form
    try:
        form = PasswordForm(request.POST)

        if not form.is_valid():
            raise Exception

        # read username + password
        username = request.user.username
        password = form.cleaned_data['password']

    except:
        ctx['alert_head'] = 'Saving failed'
        ctx['alert_text'] = 'Invalid data submitted'
        return render(request, VOTE_EDIT_TEMPLATE, ctx)


    # set the vote status to public
    try:
        vote.update_eligibility(username, password)


        vote.status.stage = Status.STAGED
        vote.status.save()
    except Exception as e:
        vote.machine_name = vote_name
        ctx['alert_head'] = 'Staging vote failed'
        ctx['alert_text'] = str(e)
        return render(request, VOTE_EDIT_TEMPLATE, ctx)

    # reload the vote props
    ctx = get_vote_props(ctx, vote)

    # done
    ctx['alert_type'] = 'success'
    ctx['alert_head'] = 'Status updated'
    ctx['alert_text'] = 'Vote has been staged. '

    return render(request, VOTE_EDIT_TEMPLATE, ctx)

@login_required
def vote_time(request, system_name, vote_name):
    # you may only use POST
    if request.method != "POST":
        raise Http404

    (system, vote, ctx) = vote_edit_context(request, system_name, vote_name)

    # if the vote is not closed, dont make it public
    if not ctx["can_set_time"]:
        ctx['alert_head'] = 'Saving failed'
        ctx['alert_text'] = 'Timings can not be changed'
        return render(request, VOTE_EDIT_TEMPLATE, ctx)

    # now try and parse the form
    try:
        form = EditScheduleForm(request.POST)

        if not form.is_valid():
            raise Exception

        # set the open / closed / public time
        open_time = form.cleaned_data["open_time"]
        close_time = form.cleaned_data["close_time"]
        public_time = form.cleaned_data["public_time"]

    except Exception as e:
        print(e, form.errors)
        ctx['alert_head'] = 'Saving failed'
        ctx['alert_text'] = 'Invalid data submitted'
        return render(request, VOTE_EDIT_TEMPLATE, ctx)


    # set the vote status to public
    try:
        vote.status.open_time = open_time
        vote.status.close_time = close_time
        vote.status.public_time = public_time
        vote.status.save()
    except Exception as e:
        ctx['alert_head'] = 'Updating times failed. '
        ctx['alert_text'] = str(e)
        return render(request, VOTE_EDIT_TEMPLATE, ctx)

    # reload the vote props
    ctx = get_vote_props(ctx, vote)

    # done
    ctx['alert_type'] = 'success'
    ctx['alert_head'] = 'Times updated'
    ctx['alert_text'] = 'Scheduling has been saved'

    return render(request, VOTE_EDIT_TEMPLATE, ctx)

@login_required
def vote_update(request, system_name, vote_name):
    # you may only use POST
    if request.method != "POST":
        raise Http404

    (system, vote, ctx) = vote_edit_context(request, system_name, vote_name)

    # if the vote is not closed, dont make it public
    if not ctx["can_update_eligibile"]:
        ctx['alert_head'] = 'Saving failed'
        ctx['alert_text'] = 'Given vote eligibility is already fixed. '
        return render(request, VOTE_EDIT_TEMPLATE, ctx)

    # now try and parse the form
    try:
        form = PasswordForm(request.POST)

        if not form.is_valid():
            raise Exception

        # read username + password
        username = request.user.username
        password = form.cleaned_data['password']

    except:
        ctx['alert_head'] = 'Saving failed'
        ctx['alert_text'] = 'Invalid data submitted'
        return render(request, VOTE_EDIT_TEMPLATE, ctx)


    # set the vote status to public
    try:
        vote.update_eligibility(username, password)
    except Exception as e:
        ctx['alert_head'] = 'Updating eligibility failed. '
        ctx['alert_text'] = str(e)
        return render(request, VOTE_EDIT_TEMPLATE, ctx)

    # reload the vote props
    ctx = get_vote_props(ctx, vote)

    # done
    ctx['alert_type'] = 'success'
    ctx['alert_head'] = 'Eligibility updated'
    ctx['alert_text'] = 'People have been re-counted. '

    return render(request, VOTE_EDIT_TEMPLATE, ctx)

@login_required
def vote_open(request, system_name, vote_name):
    # you may only use POST
    if request.method != "POST":
        raise Http404

    (system, vote, ctx) = vote_edit_context(request, system_name, vote_name)

    # if the vote is not closed, dont make it public
    if not ctx["can_set_open"]:
        ctx['alert_head'] = 'Saving failed'
        ctx['alert_text'] = 'A vote can only be set to open if there is no open time and it is already staged. '
        return render(request, VOTE_EDIT_TEMPLATE, ctx)

    # set the vote status to public
    try:
        vote.status.stage = Status.OPEN
        vote.status.save()
    except Exception as e:
        ctx['alert_head'] = 'Opening vote failed'
        ctx['alert_text'] = str(e)
        return render(request, VOTE_EDIT_TEMPLATE, ctx)

    # reload the vote props
    ctx = get_vote_props(ctx, vote)

    # done
    ctx['alert_type'] = 'success'
    ctx['alert_head'] = 'Status updated'
    ctx['alert_text'] = 'Vote has been opened. '

    return render(request, VOTE_EDIT_TEMPLATE, ctx)

@login_required
def vote_close(request, system_name, vote_name):
    # you may only use POST
    if request.method != "POST":
        raise Http404

    (system, vote, ctx) = vote_edit_context(request, system_name, vote_name)

    # if the vote is not closed, dont make it public
    if not ctx["can_set_close"]:
        ctx['alert_head'] = 'Saving failed'
        ctx['alert_text'] = 'A vote can only be set to close if there is no close time and it is already open. '
        return render(request, VOTE_EDIT_TEMPLATE, ctx)

    # set the vote status to public
    try:
        vote.status.stage = Status.CLOSE
        vote.status.save()
    except Exception as e:
        ctx['alert_head'] = 'Closing vote failed'
        ctx['alert_text'] = str(e)
        return render(request, VOTE_EDIT_TEMPLATE, ctx)

    # reload the vote props
    ctx = get_vote_props(ctx, vote)

    # done
    ctx['alert_type'] = 'success'
    ctx['alert_head'] = 'Status updated'
    ctx['alert_text'] = 'Vote has been closed. '

    return render(request, VOTE_EDIT_TEMPLATE, ctx)

@login_required
def vote_public(request, system_name, vote_name):
    # you may only use POST
    if request.method != "POST":
        raise Http404

    (system, vote, ctx) = vote_edit_context(request, system_name, vote_name)

    # if the vote is not closed, dont make it public
    if not ctx["can_set_public"]:
        ctx['alert_head'] = 'Saving failed'
        ctx['alert_text'] = 'A vote can only be set to public if there is no public time and it is already closed. '
        return render(request, VOTE_EDIT_TEMPLATE, ctx)

    # set the vote status to public
    try:
        vote.status.stage = Status.PUBLIC
        vote.status.save()
    except Exception as e:
        ctx['alert_head'] = 'Making vote public failed'
        ctx['alert_text'] = str(e)
        return render(request, VOTE_EDIT_TEMPLATE, ctx)

    # reload the vote props
    ctx = get_vote_props(ctx, vote)

    # done
    ctx['alert_type'] = 'success'
    ctx['alert_head'] = 'Status updated'
    ctx['alert_text'] = 'Vote has been made public. '

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
    auto_open_options = form.cleaned_data["auto_open_options"]
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
        vote.auto_open_options = auto_open_options

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
    ctx['alert_text'] = 'Option configuration updated. '

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
        option.picture_url = form.cleaned_data["picture_url"]
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

    vote.touch()

    # set options and the vote
    ctx['vote'] = vote
    ctx['options'] = vote.option_set.order_by('-count').annotate(percent=(F("count") * 100 /vote.passivevote.num_voters))

    if vote.status.stage != Status.PUBLIC:
        if vote.status.stage == Status.CLOSE and request.user.is_authenticated():
            if vote.system.isAdmin(request.user.profile):
                ctx['alert_type'] = 'info'
                ctx['alert_head'] = 'Non-public'
                ctx['alert_text'] = 'The results are not public yet. You can see the results because you are admin.'

                return render(request, VOTE_RESULT_TEMPLATE, ctx)

        ctx['alert_type'] = 'danger'
        ctx['alert_head'] = 'Non-public'
        ctx['alert_text'] = 'The results are not public yet. Please come back later.'

        return render(request, VOTE_ERROR_TEMPLATE, ctx)

    # render the stuff
    return render(request, VOTE_RESULT_TEMPLATE, ctx)

class VoteView(View):
    def __init__(self, preview=False):
        self.preview = preview

    @method_decorator(login_required)
    def get(self, request, system_name, vote_name):
        (system, vote) = get_vote_and_system_or_404(system_name, vote_name)

        vote.touch()

        filter = vote.filter
        status = vote.status

        error = False

        ctx = {}
        ctx['vote'] = vote

        ctx['preview'] = self.preview

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

        if (status.stage not in [Status.OPEN, Status.PUBLIC]):
            error = True

            ctx['alert_type'] = "danger"
            ctx['alert_head'] = "Not open"
            ctx['alert_text'] = "This vote is not open. Come back later."

        if self.preview:
            error = True
            ctx['alert_type'] = "info"
            ctx['alert_head'] = "Preview"
            ctx['alert_text'] = "This is a preview, so you can't vote here."

        if not error or self.preview:
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

        vote.touch()

        filter = vote.filter

        error = False

        options_obj = Option.objects.filter(id__in=options, vote__id=vote.id)

        pv = PassiveVote.objects.get(vote=vote)

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

                pv.num_voters += 1
                pv.save()

                for opt in options_obj:
                    opt.count = F('count') + 1
                    opt.save()

        ctx = {}

        ctx['page_title'] = "Vote Done"
        ctx['alert_type'] = "success"
        ctx['alert_head'] = "You voted!"
        ctx['alert_text'] = "Your votes have been counted."

        return render_to_response(VOTE_ERROR_TEMPLATE, context=ctx)
