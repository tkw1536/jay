from django.conf.urls import url
from django.views.generic import TemplateView

from . import views


urlpatterns = [
	url(r'^overview', views.overview, name='overview'),
	url(r'^create', TemplateView.as_view(template_name="vs/create_voting_system.html"), name="create"),
	url(r'^createForm', views.createForm, name='createForm'),
]