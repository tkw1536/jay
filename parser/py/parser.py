import json

# binary constants
BINARY_CONST = ['true', 'false']

# unary binary operations
UNARY_OPS = ['not']

# binary operations
FILTER_OPS = [
    'equals', 'less then', 'less then or equal', 'greater then', 'greater then or equal', 'contains', 'matches'
]

# binary operations
BINARY_OPS = [
    'and', 'or', 'nand', 'xor'
]

def clean_binary(obj):
    """
        Verifies that this is a binary filter expression.

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

    # if it is a binary constant, return it
    if op in BINARY_CONST:
        return {'operation': op}

    # if it is a unay operation
    if op in UNARY_OPS:

        # we need a right property
        if not 'right' in obj:
            return None

        # make a binary operation on the right
        right = clean_binary(obj['right'])

        # if there is nothing on the right return
        if right == None:
            return None

        # else make a clean object
        return {'operation': op, 'right': right}

    # if it is a binary operation
    if op in BINARY_OPS:

        # we need a right property
        if not 'right' in obj:
            return None

        # make a binary operation on the right
        right = clean_binary(obj['right'])

        # if there is nothing on the right return
        if right == None:
            return None

        # we need a left property
        if not 'left' in obj:
            return None

        # make a binary operation on the left
        left = clean_binary(obj['left'])

        # if there is nothing on the right return
        if left == None:
            return None

        # else make a clean object
        return {'operation': op, 'left': left, 'right': right}

    # if it is a binary operation
    if op in FILTER_OPS:
        # we need a right property
        if not 'value' in obj:
            return None

        # make a binary operation on the right
        value = clean_primtive(obj['value'])

        # if there is nothing on the right return
        if value == None:
            return None

        # we need a left property
        if not 'key' in obj:
            return None

        # make a binary operation on the left
        key = clean_primtive(obj['key'])

        # if there is nothing on the right return
        if key == None:
            return None

        # else make a clean object
        return {'operation': op, 'key': key, 'value': value}


    # otherwise we have an unknown operation
    return None


def clean_primtive(obj):
    """
        Verifies that an object is a primitive filter expression.

        obj: Object to check
    """

    # if it is not a string
    if isinstance(obj, str):
        return unicode(obj)
    if isinstance(obj, unicode):
        return obj

    # return the string itself
    return None

def simplify_operation(obj):
    """
        Does simple logical simplifications on an object.

        obj: Object to simplify
    """
    if obj['operation'] == 'and':
        # remove constants on the left and right
        left  = simplify_operation(obj['left'])
        right = simplify_operation(obj['right'])

        # find left and right operations
        left_op = left['operation']
        right_op = right['operation']

        # if the right operation is a constant
        if right_op == 'true':
            return left
        if right_op == 'false':
            return {'operation': 'false'}

        # if the left operation is a constant
        if left_op == 'true':
            return right
        if left_op == 'false':
            return {'operation': 'false'}

        # else return the cleaned operation
        return {'operation': 'and', 'left': left, 'right': right}

    if obj['operation'] == 'nand':
        # remove constants on the left and right
        left  = simplify_operation(obj['left'])
        right = simplify_operation(obj['right'])

        # find left and right operations
        left_op = left['operation']
        right_op = right['operation']

        # if the right operation is a constant
        if right_op == 'true':
            return simplify_operation({
                operation: 'not',
                'right': left
            })
        if right_op == 'false':
            return {'operation': 'true'}

        # if the left operation is a constant
        if left_op == 'true':
            return simplify_operation({
                operation: 'not',
                'right': right
            })
        if left_op == 'false':
            return {'operation': 'true'}

        # else return the cleaned operation
        return {'operation': 'and', 'left': left, 'right': right}

    if obj['operation'] == 'or':
        # remove constants on the left and right
        left  = simplify_operation(obj['left'])
        right = simplify_operation(obj['right'])

        # find left and right operations
        left_op = left['operation']
        right_op = right['operation']

        # if the right operation is a constant
        if right_op == 'true':
            return {'operation': 'true'}
        if right_op == 'false':
            return left

        # if the left operation is a constant
        if left_op == 'true':
            return {'operation': 'true'}
        if left_op == 'false':
            return right

        # else return the cleaned operation
        return {'operation': 'or', 'left': left, 'right': right}

    if obj['operation'] == 'xor':
        # remove constants on the left and right
        left  = simplify_operation(obj['left'])
        right = simplify_operation(obj['right'])

        # find left and right operations
        left_op = left['operation']
        right_op = right['operation']

        # if the right operation is a constant
        if right_op == 'true':
            # => true xor x == !x
            return simplify_operation({
                'operation': 'not',
                'right': left
            })
        if right_op == 'false':
            # => false xor x == x
            return left

        # if the left operation is a constant
        if left_op == 'true':
            return simplify_operation({
                'operation': 'not',
                'right': right
            })
        if left_op == 'false':
            return right

        # else return the cleaned operation
        return {'operation': 'or', 'left': left, 'right': right}

    if obj['operation'] == 'not':
        right = simplify_operation(obj['right'])

        # remove double nots
        if right['operation'] == 'not':
            return simplify_operation(obj['right']['right'])

        # ! nand => and
        if right['operation'] == 'nand':
            return {
                'operation': 'and',
                'left': right['left'],
                'right': right['right']
            }

        # ! and => nand
        if right['operation'] == 'and':
            return {
                'operation': 'nand',
                'left': right['left'],
                'right': right['right']
            }

        return {'operation': 'not', 'right': simplify_operation(obj['right'])}

    # else return as is
    return obj

def from_json(obj):
    """
        Parses a JSON string representing an object.

        obj: Object String to install
    """

    # try to parse the json
    try:
        jobj = json.loads(obj)
    except:
        return None

    # clean it up
    pobj = clean_binary(jobj)

    # if it fails, return none
    if pobj == None:
        return None

    # simplify it
    return simplify_operation(pobj)
