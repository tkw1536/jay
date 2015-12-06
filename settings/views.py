import json
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User
from jay.utils import superadmin
import time
from django.http import Http404
from django.db.models import Count

from .models import VotingSystem
from .forms import EditSystemForm, AddSuperAdminForm
from users.models import SuperAdmin

SETTINGS_SYSTEMS_TEMPLATE = "systems/systems_overview.html"
SETTINGS_SYSTEMS_EDIT_TEMPLATE = "systems/systems_edit.html"
SETTINGS_GLOBAL_SETTINGS_TEMPLATE = "systems/global_settings.html"

# Create your views here.
@login_required
@superadmin
def systems(request, alert_type=None, alert_head=None, alert_text=None):
	voting_system_list = VotingSystem.objects.all()

	ctx = {'voting_system_list': voting_system_list}

	# add an alert state if needed
	if alert_head or alert_text or alert_type:
		ctx['alert_type'] = alert_type
		ctx['alert_head'] = alert_head
		ctx['alert_text'] = alert_text

	return render(request, SETTINGS_SYSTEMS_TEMPLATE, ctx)

@login_required
@superadmin
def system_edit(request, system_id):

	# get the voting system object
	vs = get_object_or_404(VotingSystem, id=system_id)

	# make a context
	ctx = {'vs': vs}

	if request.method=="POST":
		try:
			# parse the form
			form = EditSystemForm(request.POST)

			if not form.is_valid():
				raise Exception
		except Exception as e:
			ctx['alert_head'] = 'Saving failed'
			ctx['alert_text'] = 'Invalid data submitted'
			print(e)

			return render(request, SETTINGS_SYSTEMS_EDIT_TEMPLATE, ctx)

		try:
			# store the fields
			vs.machine_name = form.cleaned_data['machine_name']
			vs.simple_name = form.cleaned_data['simple_name']

			# and try to clean + save
			vs.clean()
			vs.save()
		except Exception as e:
			ctx['alert_head'] = 'Saving failed'
			ctx['alert_text'] = str(e)
			return render(request, SETTINGS_SYSTEMS_EDIT_TEMPLATE, ctx)

		ctx['alert_type'] = 'success'
		ctx['alert_head'] = 'Saving suceeded'
		ctx['alert_text'] = 'Voting System saved'

	# render the response
	return render(request, SETTINGS_SYSTEMS_EDIT_TEMPLATE, ctx)

@login_required
@superadmin
def system_delete(request, system_id):
	# only POST is supported
	if request.method != "POST":
		raise Http404

	# get the voting system object
	vs = get_object_or_404(VotingSystem, id=system_id)

	# if the vote set is not empty
	if vs.vote_set.count() != 0:
		return systems(request, alert_head = "Deletion failed", alert_text="Voting System is not empty. Please delete all votes first. ")

	# try to delete
	try:
		vs.delete()
	except:
		return systems(request, alert_head = "Deletion failed")

	# done
	return systems(request, alert_type = "success", alert_head="Deletion succeeded", alert_text = "Voting System Deleted. ")

@login_required
@superadmin
def system_new(request):

	# only POST is supported
	if request.method != "POST":
		raise Http404

	# TODO: Sensible defaults
	now = str(int(time.time()))

	simple_name = 'Voting System '+now
	machine_name = 'voting_system_' + now

	# Create a new voting system
	vs = VotingSystem(simple_name=simple_name, machine_name=machine_name)

	# try to save and clean
	try:
		vs.clean()
		vs.save()
	except:
		return systems(request, alert_head="Creation failed. ", alert_text="Unable to save new VotingSystem. ")

	# redirect to the edit page
	return redirect(reverse('settings:edit', kwargs={'system_id': str(vs.id)}))


@login_required
@superadmin
def settings(request, alert_type=None, alert_head=None, alert_text=None):
	superadmin_list = SuperAdmin.objects.all()

	# exclude existing super users
	user_list = User.objects.annotate(sa=Count('superadmin')).filter(sa=0)

	ctx = {'superadmin_list': superadmin_list, 'user_list': user_list}

	if alert_head or alert_text or alert_type:
		ctx['alert_type'] = alert_type
		ctx['alert_head'] = alert_head
		ctx['alert_text'] = alert_text

	return render(request, SETTINGS_GLOBAL_SETTINGS_TEMPLATE, ctx)

@login_required
@superadmin
def superadmin_remove(request, user_id):
	
	# only POST is supported
	if request.method != "POST":
		raise Http404

	superadmin = get_object_or_404(SuperAdmin, user__id=user_id)
	current_user = request.user

	# forbidden to delete oneself
	if superadmin.user.username == current_user.username:
		return settings(request, alert_head = "Deletion failed", alert_text = "Don't torture yourself.")

	try:
		superadmin.delete()
	except:
		return settings(request, alert_head = "Deletion failed")

	return settings(request, alert_type = "success", alert_head = "Deletion succeeded", alert_text = "Super Admin Deleted.")


@login_required
@superadmin
def superadmin_add(request):

	# only POST is supported
	if request.method != "POST":
		raise Http404

	try:
		# parse the form
		form = AddSuperAdminForm(request.POST)
		if not form.is_valid():
			raise Exception
	except Exception as e:
		print(e)
		return settings(request, alert_head='Grant Failed', alert_text='Invalid data submitted')
	
	try:
		user_id = form.cleaned_data['user_id']

		# get a user object and construct a new super admin
		user = get_object_or_404(User, id=user_id)
		superadmin = SuperAdmin(user=user)
		
		# clean + save
		superadmin.clean()
		superadmin.save()
	except Exception as e:
		print(e)
		return settings(request, alert_head="Grant Failed", alert_text="Unable to make user " + str(user.username) +" a super admin. ")

	return settings(request, alert_type = "success", alert_head = "Grant succeeded", alert_text = "User " + str(user.username) + " is a super admin now.")






