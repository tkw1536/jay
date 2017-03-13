import re
import PreJsPy

OP_TRUE = ['true']
OP_FALSE = ['false']

OP_NOT = ['not', '!']

OP_EQUALS = ['equals', '=', '==', '===']

OP_LESS = ['less than', '<']
OP_LESS_EQUAL = ['less than or equal', '<=', '=<', ]

OP_GREATER = ['greater than', '>']
OP_GREATER_EQUAL = ['greater than or equal', '>=', '=>']

OP_CONTAINS = ['contains', '::']

OP_MATCHES = ['matches', 'unicorn', '@']

OP_AND = ['and', '&', '&&', '*']

OP_OR = ['or', '|', '||', '+']

OP_NAND = ['nand', '!&']

OP_XOR = ['xor', '^']

# =============================================================================
# OPERATOR GROUPS CONFIG
# =============================================================================

# unary operators that expect one binary argument
OPS_UNARY = [] + OP_NOT

# filters that expect a key and value argument
OPS_FILTERS = [] + OP_EQUALS + OP_LESS + OP_LESS_EQUAL + OP_GREATER + \
              OP_GREATER_EQUAL + OP_CONTAINS + OP_MATCHES

# binary operators that expect to logical arguments
OPS_BINARY = [] + OP_AND + OP_OR + OP_NAND + OP_XOR


# =============================================================================


def popu_jsep(jsep):
    jsep.setUnaryOperators(OPS_UNARY)

    OPS_BIN_ALL = dict((o, 1) for o in OPS_BINARY)
    OPS_BIN_ALL.update(
        dict((o, 2) for o in OPS_FILTERS)
    )
    jsep.setBinaryOperators(OPS_BIN_ALL)


# create a new parser for parsing all the things
parser = PreJsPy.PreJsPy()
popu_jsep(parser)


def parse_binary(tree):
    """
      A binary expression is either:

      1. A literal expression
        1a. the literal true  ( ===> true )
        1b. the literal false ( ===> false )
        1c. the literal null ( ===> false )
      2. A unary logical expression
        2a. a not expression
      3. A binary logical connetive
        3a. a logical And
        3b. a logical or
        3c. a logical nand
        3d. a logical xor
      4. A binary filter
        4a. an equals filter
        4b. a less filter
        4c. a less or equals filter
        4d. a greater filter
        4e. a greater than filter
        4f. a contains filter
        4g. a matches filter
      5. A primitive expression ( ==> is the string false-ish ? )
    """

    # if there is nothing, return
    if not tree:
        raise Exception("Missing binary expression. ")

    # check for literals
    if tree["type"] == "Literal":
        if tree["raw"] == OP_TRUE[0]:
            return {'operation': OP_TRUE[0]}
        elif (tree["raw"] == OP_FALSE[0]):
            return {'operation': OP_FALSE[0]}
        elif (tree.raw == 'null'):
            return {'operation': OP_FALSE[0]}

    # check for a unary expression
    if (tree["type"] == 'UnaryExpression'):
        # find the index inside the logical not
        if tree["operator"] in OP_NOT:
            return {'operation': OP_NOT[0],
                    'right': parse_binary(tree["argument"])}
        else:
            raise Exception(
                'Expected a binary expression, but found unknown UnaryExpression type in input. ')

    # check for binary logical connectives
    if (tree["type"] == 'BinaryExpression' or tree[
        "type"] == 'LogicalExpression'):

        # check for a logical and
        if tree["operator"] in OP_AND:
            return {'operation': OP_AND[0], 'left': parse_binary(tree["left"]),
                    'right': parse_binary(tree["right"])}

        # check for a logical or
        if tree["operator"] in OP_OR:
            return {'operation': OP_OR[0], 'left': parse_binary(tree["left"]),
                    'right': parse_binary(tree["right"])}

        # check for a logical nand
        if tree["operator"] in OP_NAND:
            return {'operation': OP_NAND[0],
                    'left': parse_binary(tree["left"]),
                    'right': parse_binary(tree["right"])}

        # check for a logical xor
        if tree["operator"] in OP_XOR:
            return {'operation': OP_XOR[0], 'left': parse_binary(tree["left"]),
                    'right': parse_binary(tree["right"])}

    # check for binary filter
    if (tree["type"] == 'BinaryExpression' or tree[
        "type"] == 'LogicalExpression'):
        # an equals filter
        if tree["operator"] in OP_EQUALS:
            return {'operation': OP_EQUALS[0],
                    'key': parse_primitive(tree["left"]),
                    'value': parse_primitive(tree["right"])}

        # a less filter
        if tree["operator"] in OP_LESS:
            return {'operation': OP_LESS[0],
                    'key': parse_primitive(tree["left"]),
                    'value': parse_primitive(tree["right"])}

        # a less or equals filter
        if tree["operator"] in OP_LESS_EQUAL:
            return {'operation': OP_LESS_EQUAL[0],
                    'key': parse_primitive(tree["left"]),
                    'value': parse_primitive(tree["right"])}

        # a greater filter
        if tree["operator"] in OP_GREATER:
            return {'operation': OP_GREATER[0],
                    'key': parse_primitive(tree["left"]),
                    'value': parse_primitive(tree["right"])}

        # a greater or equals filter
        if tree["operator"] in OP_GREATER_EQUAL:
            return {'operation': OP_GREATER_EQUAL[0],
                    'key': parse_primitive(tree["left"]),
                    'value': parse_primitive(tree["right"])}

        # a contains filter
        if tree["operator"] in OP_CONTAINS:
            return {'operation': OP_CONTAINS[0],
                    'key': parse_primitive(tree["left"]),
                    'value': parse_primitive(tree["right"])}

        # a matches filter
        if tree["operator"] in OP_MATCHES:
            return {'operation': OP_MATCHES[0],
                    'key': parse_primitive(tree["left"]),
                    'value': parse_primitive(tree["right"])}

        raise Exception(
            'Expected a binary expression, but found unknown BinaryExpression / LogicalExpression in input. ');

    is_primitive = False

    try:
        parse_primitive(tree)
        is_primitive = True
    except:
        pass

    if is_primitive:
        raise Exception(
            "Expected a binary expression, but found a primitive instead. ")
    else:
        raise Exception(
            "Expected a binary expression, but found unknown expression type in input. ")


def parse_primitive(tree):
    """
    A primitive expression is either:

      1. A ThisExpression ( ==> this )
      1. A literal expression ( ==> literal.raw )
      2. A identifier expression ( ==> identifier.name )
      3. A non-empty compound expression consisting of primitives as above ( ==> join as strings )

    """

    # if there is nothing, return
    if not tree:
        raise Exception('Missing binary expression. ')

    # check for a literal expression
    if (tree["type"] == 'Literal'):
        if isinstance(tree["value"], str):
            return tree["value"]
        else:
            return tree["raw"]

    # check for an identifier
    if tree["type"] == "Identifier":
        return tree["name"]

    # in case of a compound expression
    if tree["type"] == "CompoundExpression":
        return " ".join([parse_primitive(e) for e in tree["body"]])

    raise Exception(
        "Expected a primitive expression, but found unknown expression type in input. ")


def parse(s):
    """
    Parses a string into an expression
    """

    ast = parser.parse(s)

    return parse_binary(ast)


def matches_logical(tree, obj):
    """ Check if an object matches a logical tree """

    # operation of the tree
    op = tree['operation']

    # constants
    if op == OP_TRUE[0]:
        return True

    if op == OP_FALSE[0]:
        return False

    # not
    if op == OP_NOT[0]:
        return not matches_logical(tree["right"], obj)

    # binary operations
    if op == OP_AND[0]:
        return matches_logical(tree['left'], obj) and matches_logical(
            tree['right'], obj)

    if op == OP_NAND[0]:
        return not (
            matches_logical(tree['left'], obj) and matches_logical(
                tree['right'],
                obj))

    if op == OP_OR[0]:
        return matches_logical(tree['left'], obj) or matches_logical(
            tree['right'], obj)

    if (op == OP_XOR[0]):
        return matches_logical(tree['left'], obj) != matches_logical(
            tree['right'], obj)

    return matches_filter(tree, obj)


def match_toString(obj):
    if obj is bool(obj):
        return "true" if obj is True else "false"
    return str(obj)


def match_toFloat(obj):
    return float(obj)


def matches_filter(tree, obj):
    """ Check if a tree matches a filter

    :param tree:
    :param obj:
    :return:
    """

    # find the operation
    op = tree['operation']

    # find the key and value to check.
    key = tree['key']
    value = tree['value']

    # if the object does not have the property, we can exit immediatly
    if (not key in obj):
        return False

    # read the key from the object
    obj_value = obj[key]

    # equality: check if the objects are equal as strings.
    if op in OP_EQUALS:
        return match_toString(obj_value) == match_toString(value)

    # numeric comparisions
    if op in OP_LESS:
        try:
            value = match_toFloat(value)
            obj_value = match_toFloat(obj_value)
        except:
            return False

        return obj_value < value

    if op in OP_LESS_EQUAL:
        try:
            value = match_toFloat(value)
            obj_value = match_toFloat(obj_value)
        except:
            return False

        return obj_value <= value

    if op in OP_GREATER:
        try:
            value = match_toFloat(value)
            obj_value = match_toFloat(obj_value)
        except:
            return False

        return obj_value > value

    if (op == OP_GREATER_EQUAL[0]):
        try:
            value = match_toFloat(value)
            obj_value = match_toFloat(obj_value)
        except:
            return False

        return obj_value >= value

    # check if we match a regular expression
    if op in OP_MATCHES:
        try:
            value = re.compile(value)
        except:
            return False

        return bool(value.match(match_toString(obj_value)))

    # check if a value is contained in this array
    if op in OP_CONTAINS:
        return value in obj_value

    # and thats it
    return False


def matches(tree, obj):
    """Checks if a tree matches an object"""

    return matches_logical(tree, obj)


op_list = {
    'OP_TRUE': OP_TRUE,
    'OP_FALSE': OP_FALSE,

    'OP_NOT': OP_NOT,

    'OP_EQUALS': OP_EQUALS,

    'OP_LESS': OP_LESS,
    'OP_LESS_EQUAL': OP_LESS_EQUAL,

    'OP_GREATER': OP_GREATER,
    'OP_GREATER_EQUAL': OP_GREATER_EQUAL,

    'OP_CONTAINS': OP_CONTAINS,

    'OP_MATCHES': OP_MATCHES,

    'OP_AND': OP_AND,

    'OP_OR': OP_OR,

    'OP_NAND': OP_NAND,

    'OP_XOR': OP_XOR,

    'OPS_UNARY': OPS_UNARY,
    'OPS_FILTERS': OPS_FILTERS,
    'OPS_BINARY': OPS_BINARY
}

__all__ = ['parse', 'matches', 'op_list']
