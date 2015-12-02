from django.conf.urls import include, url

from django.views.generic import TemplateView

from votes.views import VoteView, results, system_home

urlpatterns = [
    url(r'^$', system_home, name="system"),
    url(r'^(?P<vote_name>[\w-]+)$', VoteView.as_view(), name="vote"),
    url(r'^(?P<vote_name>[\w-]+)/results$', results, name="results"),
]
