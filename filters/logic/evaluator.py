def composite(tree, obj):
    """
        Checks if a primitive tree matches an object.

        tree: primitive tree to check against.
        obj: Object to check matching against.
    """
    # read operation to perform
    op = tree['operation']

    # not
    if op == 'not':
        return not composite(tree['right'], obj)

    if op == 'and':
        return (composite(tree['left'], obj) and composite(tree['right'], obj))

    if op == 'nand':
        return not (composite(tree['left'], obj) and composite(tree['right'], obj))

    if op == 'or':
        return composite(tree['left'], obj) or composite(tree['right'], obj)

    if op == 'xor':
        return composite(tree['left'], obj) ^ composite(tree['right'], obj)

    if op == 'true':
        return True

    if op == 'false':
        return False

    # it is not a composite operation => use it as a primitive
    return primitive(tree, obj)

def primitive(tree, obj):
    """
        Checks if a primtive primitive matches an object.

        tree: Primitive primitive tree to check against.
        obj: Object to check matching against.
    """

    # read the operation to perform
    op = tree['operation']

    # read key and value to check
    key = tree['key']
    value = tree['value']

    # if the key is not the key, return False
    if not key in obj:
        return False

    # read the key from the object
    obj_key = obj[key]

    if op == 'equals':
        # check for string equality
        return str(obj_key) == str(value)

    if op == 'less then':
        # parse both object and value as a float
        try:
            value = float(value)
            obj_key = float(obj_key)
        except:
            return False

        # check for less
        return obj_key < value

    if op == 'less then or equal':
        # parse both object and value as a float
        try:
            value = float(value)
            obj_key = float(obj_key)
        except:
            return False

        # check for less equal
        return obj_key <= value

    if op == 'greater then':
        # parse both object and value as a float
        try:
            value = float(value)
            obj_key = float(obj_key)
        except:
            return False

        # check for greater
        return obj_key > value

    if op == 'greater then or equal':
        # parse both object and value as a float
        try:
            value = float(value)
            obj_key = float(obj_key)
        except:
            return False

        # check for greater or equal
        return obj_key >= value

    if op == 'contains':
        try:
            # check if the key can be found somewhere in the value
            return obj_key.index(value) >= 0
        except:
            return False

    if op == 'matches':
        try:
            # trun the value into a string
            obj_key = str(obj_key)

            # check if that value matches the regular expression
            return (True if re.match(value, obj_key) else False)
        except:
            return False

    # we have an unsupported primitive, so we assume it does not match at all
    return False
