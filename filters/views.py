from django.shortcuts import render, get_object_or_404, redirect
from django.core.exceptions import PermissionDenied
from django.core.urlresolvers import reverse

from filters.models import UserFilter
from votes.models import VotingSystem

from jay.utils import priviliged

from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator

FILTER_MAIN_VIEW = "filters/forest.html"

@login_required
@priviliged
def Forest(request, alert_head=None, alert_text=None):
    # if the user does not have enough priviliges, throw an exception
    if not request.user.profile.isElevated():
        raise PermissionDenied
    
    # build a new context
    ctx = {}

    # get all the voting systems for this user
    admin_systems = request.user.profile.getAdministratedSystems()

    # and all the other ones also
    other_systems = list(filter(lambda a: not a in admin_systems, VotingSystem.objects.all()))
        
    # give those to the view
    ctx['admin_systems'] = admin_systems
    ctx['other_systems'] = other_systems
    
    # add an alert state if needed
    if alert_head or alert_text:
        ctx['alert_head'] = alert_head
        ctx['alert_text'] = alert_text
    
    return render(request, FILTER_MAIN_VIEW, ctx)

@login_required
def FilterNew(request, system_name):
    # get the votingsystem
    system = get_object_or_404(VotingSystem, machine_name=system_name)
    
    # check if the user can edit it. 
    # if not, go back to the overview
    if not system.canEdit(request.user.profile):
        return Forest(request, alert_head="Creation failed", alert_text="Nice try. You are not allowed to edit this VotingSystem. ")
    
    # create a new filter
    newFilter = UserFilter(system=system, name="Unnamed User Filter", value="true")
    
    # save the filter in the database
    try:
        newFilter.save()
    except:
        return Forest(request, alert_head="Unable to store new user object. ")
    
    # and redirect to the edit page
    return redirect(reverse('filters:edit', kwargs={'filter_id': newFilter.id}))

@login_required
def FilterDelete(request, filter_id):
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
    
    # redirect back to the forest page. 
    return redirect(reverse('filters:forest'))

@login_required
@priviliged
def FilterTest(request, filter_id):
    # try and grab the user filter
    filter = get_object_or_404(UserFilter, id=filter_id)
    return Forest(request, alert_head="Unimplemented")
    

@login_required
def FilterEdit(request, filter_id):
    # try and grab the user filter
    filter = get_object_or_404(UserFilter, id=filter_id)
    return Forest(request, alert_head="Unimplemented")
