from django.conf.urls import include, url

from django.views.generic import TemplateView

from votes.views import *

urlpatterns = [
    # Home for the votes
    url(r'^$', system_home, name="system"),

    # adding / removing admins
    url(r'^admins$', admin, name="admins"),
    url(r'^admins/add$', admin_add, name="admins_add"),
    url(r'^admins/remove$', admin_remove, name="admins_remove"),

    # adding a vote
    url(r'^add/$', vote_add, name="add"),

    # vote and results
    url(r'^(?P<vote_name>[\w-]+)/', include([
        url(r'^$', VoteView.as_view(), name="vote"),
        url(r'^results$', results, name="results"),

        # editing a vote
        url(r'^edit$', vote_edit, name="edit"),
        url(r'^delete$', vote_delete, name="delete"),
        url(r'^edit/filter$', vote_filter, name="edit_filter"),
        url(r'^edit/options$', vote_option, name="edit_options"),

        url(r'^edit/stage$', vote_time, name="edit_time"),
        url(r'^edit/stage/stage$', vote_stage, name="edit_stage"),
        url(r'^edit/stage/update$', vote_update, name="edit_update"),
        url(r'^edit/stage/open$', vote_open, name="edit_open"),
        url(r'^edit/stage/close$', vote_close, name="edit_close"),
        url(r'^edit/stage/public$', vote_public, name="edit_public"),

        # Options for a vote
        url(r'^edit/options/add$', vote_options_add, name="option_add"),
        url(r'^edit/options/edit$', vote_options_edit, name="option_edit"),
        url(r'^edit/options/up$', vote_options_up, name="option_up"),
        url(r'^edit/options/down$', vote_options_down, name="option_down"),
        url(r'^edit/options/delete$', vote_options_remove, name="option_delete")
    ])),
]
