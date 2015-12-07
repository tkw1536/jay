import datetime
from django import template

register = template.Library()

@register.filter()
def can_edit(vote_or_vs, user):
    return vote_or_vs.canEdit(user)

@register.filter()
def can_delete(vote_or_vs, user):
    return vote_or_vs.canDelete(user)
