# composite constants
LOGICAL_CONST = ['true', 'false']
# unary composite operations
UNARY_OPS = ['not']

# composite operations
FILTER_OPS = [
    'equals', 'less then', 'less then or equal', 'greater then', 'greater then or equal', 'contains', 'matches'
]

# composite operations
LOGICAL_BINARY = [
    'and', 'or', 'nand', 'xor'
]

def composite(obj):
    """
        Verifies that this is a composite filter expression.

        obj: Object to check
    """

    # it needs to be a dictonary
    if type({}) != dict:
        return False

    # we need an operation key
    if not 'operation' in obj:
        return None

    # check which operation it is
    op = obj['operation']

    # if it is a composite constant, return it
    if op in LOGICAL_CONST:
        return {'operation': op}

    # if it is a unay operation
    if op in UNARY_OPS:

        # we need a right property
        if not 'right' in obj:
            return None

        # make a composite operation on the right
        right = composite(obj['right'])

        # if there is nothing on the right return
        if right == None:
            return None

        # else make a clean object
        return {'operation': op, 'right': right}

    # if it is a composite operation
    if op in LOGICAL_BINARY:

        # we need a right property
        if not 'right' in obj:
            return None

        # make a composite operation on the right
        right = composite(obj['right'])

        # if there is nothing on the right return
        if right == None:
            return None

        # we need a left property
        if not 'left' in obj:
            return None

        # make a composite operation on the left
        left = composite(obj['left'])

        # if there is nothing on the right return
        if left == None:
            return None

        # else make a clean object
        return {'operation': op, 'left': left, 'right': right}

    # if it is a composite operation
    if op in FILTER_OPS:
        # we need a right property
        if not 'value' in obj:
            return None

        # make a primitive operation on the right
        value = primitive(obj['value'])

        # if there is nothing on the right return
        if value == None:
            return None

        # we need a left property
        if not 'key' in obj:
            return None

        # make a primitive operation on the left
        key = primitive(obj['key'])

        # if there is nothing on the right return
        if key == None:
            return None

        # else make a clean object
        return {'operation': op, 'key': key, 'value': value}


    # otherwise we have an unknown operation
    return None

def primitive(obj):
    """
        Verifies that an object is a primitive filter object.

        obj: Object to check
    """

    # if it is not a string
    if isinstance(obj, str):
        return unicode(obj)
    if isinstance(obj, unicode):
        return obj

    # return the string itself
    return None
