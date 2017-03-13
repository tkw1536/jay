from django.conf.urls import url
from django.views.generic import TemplateView

from settings.views import systems

urlpatterns = [

	# Superadmin management
	#url(r'^$', superadmins.settings, name="settings"),
	#url(r'^superadmins/add$', superadmins.superadmin_add, name="add"),
	#url(r'^superadmins/(?P<user_id>[\w-]+)/remove$', superadmins.superadmin_remove, name="remove"),
	
	# System management
	url(r'^systems$', systems.systems, name='systems'),
	url(r'^systems/new$', systems.system_new, name="new"),
	url(r'^systems/(?P<system_id>[\w-]+)/delete$', systems.system_delete, name="delete"),
	url(r'^systems/(?P<system_id>[\w-]+)$', systems.system_edit, name="edit"),
]
