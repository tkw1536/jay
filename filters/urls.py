from django.conf.urls import include, url

from django.views.generic import TemplateView
from filters.views import Forest, FilterNew, FilterTest, FilterEdit, FilterDelete

urlpatterns = [
    url(r'^$', Forest),
    url(r'^new$', Forest, name="filter_new"),

    url(r'^(?P<filter_id>[\w-]+)$', FilterTest, name="filter_test"),
    url(r'^(?P<filter_id>[\w-]+)/edit$', FilterEdit, name="filter_edit"),
    url(r'^(?P<filter_id>[\w-]+)/delete$', FilterDelete, name="filter_delete"),
]
