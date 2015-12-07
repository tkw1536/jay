from django.core.exceptions import ValidationError

RESTRICTED_WORDS = [
    # MASTER
    'djangoadmin', 'imprint', 'privacy', 'about', 'help', 'filters', 'login', 'logout', 'settings', 

    # filters
    'new', 'edit', 'delete', 'testuser',

    # settings
    'superadmins', 'add', 'remove', 'new',

    # Votes
    'settings', 'admins', 'add', 'remove', 'results', 'edit', 'delete', 'filter', 'options', 'stage', 'update', 'open', 'close', 'public', 'up', 'down',

    # Static
    'static'
]

def is_restricted_word(name, value):
    """
        Checks if an identifier contains a restricted word.
    """

    rvalue = value.lower().strip()

    if rvalue in RESTRICTED_WORDS:
        raise ValidationError({
            name: ValidationError('Value for \''+name+'\' invalid: \''+rvalue+'\' can not be used as an identifier. ', code='invalid')
        })
