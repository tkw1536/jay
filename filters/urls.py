from django.conf.urls import include, url

from django.views.generic import TemplateView
from filters.views import Forest, FilterNew, FilterTest, FilterTestUser, FilterEdit, FilterDelete

urlpatterns = [
    url(r'^$', Forest, name="forest"),
    url(r'^new$', FilterNew, name="new"),
    url(r'^(?P<filter_id>[\w-]+)/edit$', FilterEdit, name="edit"),
    url(r'^(?P<filter_id>[\w-]+)/delete$', FilterDelete, name="delete"),
    url(r'^(?P<filter_id>[\w-]+)/testuser$', FilterTestUser, name="testuser"),
    url(r'^(?P<filter_id>[\w-]+)$', FilterTest, name="test"),
]
