from django.shortcuts import render

from filters.models import UserFilter
from votes.models import VotingSystem

from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator

FILTER_MAIN_VIEW = "filters/forest.html"

@login_required
def Forest(request):
    ctx = {}
    
    # get all the voting systems for this user
    admin_systems = request.user.profile.getAdministratedSystems()
    
    # and all the other ones also
    other_systems = VotingSystem.objects.all().exclude(*admin_systems)
    
    
    # give those to the view
    ctx['admin_systems'] = admin_systems
    ctx['other_systems'] = other_systems
    
    return render(request, FILTER_MAIN_VIEW, ctx)