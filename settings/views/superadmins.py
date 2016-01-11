from django.shortcuts import render, get_object_or_404, redirect

from django.http import Http404

from django.db.models import Count

from django.contrib.auth.decorators import login_required
from jay.utils import superadmin

from django.contrib.auth.models import User
from users.models import SuperAdmin

from settings.forms import AddSuperAdminForm

SETTINGS_GLOBAL_SETTINGS_TEMPLATE = "systems/global_settings.html"

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
		return settings(request, alert_head="Grant Failed", alert_text="Unable to make user " + str(user.username) +" a super admin. ")

	return settings(request, alert_type = "success", alert_head = "Grant succeeded", alert_text = "User " + str(user.username) + " is a super admin now.")