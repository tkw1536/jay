from django.conf.urls import url
from django.views.generic import TemplateView

from . import views


urlpatterns = [
	# TODO: Gloabl settings view
	url(r'^systems$', views.systems, name='systems'),
	url(r'^systems/new$', views.system_new, name="new"),
	url(r'^systems/(?P<system_id>[\w-]+)/delete$', views.system_delete, name="delete"),
	url(r'^systems/(?P<system_id>[\w-]+)$', views.system_edit, name="edit"),
]
