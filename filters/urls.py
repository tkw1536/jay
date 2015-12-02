from django.conf.urls import include, url

from django.views.generic import TemplateView
from filters.views import Forest, FilterNew, FilterTest, FilterEdit, FilterDelete

urlpatterns = [
    url(r'^$', Forest, name="forest"),
    url(r'^new/(?P<system_name>[\w-]+)$', FilterNew, name="new"),
    url(r'^(?P<filter_id>[\w-]+)$', FilterTest, name="test"),
    url(r'^(?P<filter_id>[\w-]+)/edit$', FilterEdit, name="edit"),
    url(r'^(?P<filter_id>[\w-]+)/delete$', FilterDelete, name="delete"),
]
