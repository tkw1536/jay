from django.conf.urls import include, url
from django.contrib import admin

from django.views.generic import TemplateView

urlpatterns = [
    url(r'^$', TemplateView.as_view(template_name="base/base.html")),
    url(r'^vote$', TemplateView.as_view(template_name="vote/vote_vote.html")),
]