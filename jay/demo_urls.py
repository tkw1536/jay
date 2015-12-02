from django.conf.urls import include, url

from django.views.generic import TemplateView

from . import demo_views
# from settings.models import VotingSystem
from settings import views 

urlpatterns = [
    url(r'^$', TemplateView.as_view(template_name="base/base.html")),
    url(r'^vote/(?P<vote_name>[\w-]+)$', demo_views.vote),
]
