from django.core.exceptions import ValidationError

RESTRICTED_WORDS = [
    'settings',
    'demo',
    'imprint',
    'privacy',
    'help',
    'filters',
    'login',
    'logout',
    'edit'
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
