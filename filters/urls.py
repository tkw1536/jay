from django.conf.urls import include, url

from django.views.generic import TemplateView
from filters.views import Forest

urlpatterns = [
    url(r'^$', Forest),
]
