from django.conf.urls import include, url

from django.views.generic import TemplateView

from votes.views import *

urlpatterns = [
    # Home for the votes
    url(r'^$', system_home, name="system"),

    # vote manager for a system
    url(r'^settings$', system_settings, name="settings"),

    # adding / removing admins
    url(r'^admins/add$', admin_add, name="admins_add"),
    url(r'^admins/remove$', admin_remove, name="admins_remove"),

    # adding a vote
    url(r'^add/$', vote_add, name="add"),

    # vote and results
    url(r'^(?P<vote_name>[\w-]+)/$', VoteView.as_view(), name="vote"),
    url(r'^(?P<vote_name>[\w-]+)/results$', results, name="results"),

    # editing a vote
    url(r'^(?P<vote_name>[\w-]+)/edit$', vote_edit, name="edit"),
    url(r'^(?P<vote_name>[\w-]+)/edit/filter$', vote_filter, name="edit_filter"),
    url(r'^(?P<vote_name>[\w-]+)/edit/options$', vote_option, name="edit_options"),

    url(r'^(?P<vote_name>[\w-]+)/edit/stage/open$', vote_open, name="edit_open"),
    url(r'^(?P<vote_name>[\w-]+)/edit/stage/close$', vote_close, name="edit_close"),
    url(r'^(?P<vote_name>[\w-]+)/edit/stage/public$', vote_public, name="edit_public"),

    # Options for a vote
    url(r'^(?P<vote_name>[\w-]+)/edit/options/add$', vote_options_add, name="option_add"),
    url(r'^(?P<vote_name>[\w-]+)/edit/options/edit$', vote_options_edit, name="option_edit"),
    url(r'^(?P<vote_name>[\w-]+)/edit/options/up$', vote_options_up, name="option_up"),
    url(r'^(?P<vote_name>[\w-]+)/edit/options/down$', vote_options_down, name="option_down"),
    url(r'^(?P<vote_name>[\w-]+)/edit/options/delete$', vote_options_remove, name="option_delete")
]
