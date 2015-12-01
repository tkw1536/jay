from django.conf.urls import include, url

from django.views.generic import TemplateView

from votes.views import VoteView, results

urlpatterns = [
    url(r'^(?P<vote_name>[\w-]+)$', VoteView.as_view(), name="vote"),
    url(r'^(?P<vote_name>[\w-]+)/results$', results, name="results"),
]
