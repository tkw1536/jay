from django.core.exceptions import PermissionDenied, ValidationError

from django.core.urlresolvers import reverse
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User


from django.http import Http404

from filters.models import UserFilter
from filters.forms import NewFilterForm, EditFilterForm, FilterTestForm, FilterTestUserForm
import filters.forest as forest

import json


from votes.models import VotingSystem

from jay.utils import priviliged

FILTER_FOREST_TEMPLATE = "filters/filter_forest.html"
FILTER_EDIT_TEMPLATE = "filters/filter_edit.html"
FILTER_TEST_TEMPLATE = "filters/filter_test.html"

@login_required
@priviliged
def Forest(request, alert_type=None, alert_head=None, alert_text=None):

    # if the user does not have enough priviliges, throw an exception
    if not request.user.profile.isElevated():
        raise PermissionDenied

    # build a new context
    ctx = {}

    (admin_systems, other_systems) = request.user.profile.getSystems()

    # give those to the view
    ctx['admin_systems'] = admin_systems
    ctx['other_systems'] = other_systems

    # add an alert state if needed
    if alert_head or alert_text or alert_type:
        ctx['alert_type'] = alert_type
        ctx['alert_head'] = alert_head
        ctx['alert_text'] = alert_text

    return render(request, FILTER_FOREST_TEMPLATE, ctx)

@login_required
def FilterNew(request):
    # we need some post data, otherwise it wont work.
    if request.method != "POST":
        raise Http404

    # try to parse the form
    try:
        form = NewFilterForm(request.POST)

        # Woopsie
        if not form.is_valid():
            raise Exception

        system_name = form.cleaned_data['system_name']
    except:
        return Forest(request, alert_head="Creation failed", alert_text="Invalid data submitted. ")

    # get the votingsystem
    system = get_object_or_404(VotingSystem, machine_name=system_name)

    # check if the user can edit it.
    # if not, go back to the overview
    if not system.canEdit(request.user.profile):
        return Forest(request, alert_head="Creation failed", alert_text="Nice try. You are not allowed to edit this VotingSystem. ")

    # create a new filter
    # TODO: Make a better default name
    newFilter = UserFilter(system=system, name="Unnamed User Filter", value="true")

    # save the filter in the database
    try:
        newFilter.clean()
        newFilter.save()
    except:
        return Forest(request, alert_head="Unable to store new user object. ")

    # and redirect to the edit page
    return redirect(reverse('filters:edit', kwargs={'filter_id': newFilter.id}))

@login_required
def FilterDelete(request, filter_id):

    # we need some post data, otherwise it wont work.
    if request.method != "POST":
        raise Http404

    #  try and grab the user filter
    filter = get_object_or_404(UserFilter, id=filter_id)

    # find the corresponding voting system.
    system = filter.system

    # check if the user can edit it.
    # if not, go back to the overview
    if not system.canEdit(request.user.profile):
        return Forest(request, alert_head="Deletion failed", alert_text="Nice try. You don't have permissions to delete this voting system. ")

    # check that no voting system is using this filter before deleting.
    if filter.vote_set.count() > 0:
        return Forest(request, alert_head="Deletion failed", alert_text="There is still a vote using this filter. You can not delete it right now. ")

    # Delete the item
    try:
        filter.delete()
    except:
        return Forest(request, alert_head="Deletion failed")

    # show the forest page
    return Forest(request, alert_type="success", alert_head="Deletion successful", alert_text="The filter has been deleted. ")

@login_required
@priviliged
def FilterEdit(request, filter_id):
    # make a context
    ctx = {}

    # try and grab the user filter and put it in the filter
    filter = get_object_or_404(UserFilter, id=filter_id)
    ctx["filter"] = filter

    # check if the user can edit it
    if not filter.canEdit(request.user.profile):
        raise PermissionDenied

    # Set up the breadcrumbs
    bc = []
    bc.append({'url':reverse('home'), 'text':'Home'})
    bc.append({'url':reverse('filters:forest'), 'text':'Filters'})
    bc.append({'url':filter.get_absolute_url(), 'text':filter.name, 'active':True})

    ctx['breadcrumbs'] = bc


    if request.method == "POST":
        # parse the post data from the form
        try:
            form = EditFilterForm(request.POST)

            if not form.is_valid():
                raise Exception
        except:
            ctx['alert_head'] = 'Saving failed'
            ctx['alert_text'] = 'Invalid data submitted'
            return render(request, FILTER_EDIT_TEMPLATE, ctx)

        # check if we have a valid tree manually
        try:
            tree = forest.parse(form.cleaned_data['value'])
            if not tree:
                raise Exception
        except Exception as e:
            ctx['alert_head'] = 'Saving failed'
            ctx['alert_text'] = str(e)
            return render(request, FILTER_EDIT_TEMPLATE, ctx)

        # write the name and value, then save it in the database
        try:
            # store the name and value
            filter.name = form.cleaned_data['name']
            filter.value = form.cleaned_data['value']

            # and try to clean + save
            filter.clean()
            filter.save()
        except Exception as e:
            ctx['alert_head'] = 'Saving failed'
            ctx['alert_text'] = str(e)
            return render(request, FILTER_EDIT_TEMPLATE, ctx)

        # be done
        ctx['alert_type'] = 'success'
        ctx['alert_head'] = 'Saving suceeded'
        ctx['alert_text'] = 'Filter saved'

    # render all the stuff
    return render(request, FILTER_EDIT_TEMPLATE, ctx)

@login_required
@priviliged
def FilterTest(request, filter_id, obj = None):
    # try and grab the user filter
    filter = get_object_or_404(UserFilter, id=filter_id)

    if obj == None:
        obj = '{}'

        # if we have some post data try and parse it
        if request.method == "POST":
            try:
                form = FilterTestForm(request.POST)
                if form.is_valid():
                    obj = form.cleaned_data["test_obj"]
            except:
                pass

    ctx = {
        'obj': obj,
        'usernames': User.objects.values_list("username", flat=True),
        'filter': filter
    }

    return render(request, FILTER_TEST_TEMPLATE, ctx)

@login_required
@priviliged
def FilterTestUser(request, filter_id):
    # try and grab the user filter
    filter = get_object_or_404(UserFilter, id=filter_id)

    obj = '{}'

    # only post is supported
    if request.method != "POST":
        raise Http404

    try:
        form = FilterTestUserForm(request.POST)
        if form.is_valid():
            obj = form.cleaned_data["user"]
            obj = User.objects.filter(username=obj)[0].profile.details
    except Exception as e:
        print(e)
        pass

    return FilterTest(request, filter_id, obj = obj)
