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

    print(*admin_systems)

    # and all the other ones also
    other_systems = list(filter(lambda a: not a in admin_systems, VotingSystem.objects.all()))

    # give those to the view
    ctx['admin_systems'] = admin_systems
    ctx['other_systems'] = other_systems

    return render(request, FILTER_MAIN_VIEW, ctx)

def FilterNew(request, filter_id):
    pass

def FilterTest(request, filter_id):
    pass

def FilterEdit(request, filter_id):
    pass

def FilterDelete(request, filter_id):
    pass
