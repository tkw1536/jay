from . import logic


def layouter(tree, obj):
    op = tree["operation"]

    # we have a constant or a filter, there is only one thing to render
    if ((op in logic.op_list["OP_TRUE"]) or (
        op in logic.op_list["OP_FALSE"]) or (
        op in logic.op_list["OPS_FILTERS"])):
        return layout_const(op, tree, obj)

    # for a unary operation, we add a new node on top
    if (op in logic.op_list["OPS_UNARY"]):
        right = layouter(tree["right"], obj)
        return layout_unary(op, right, tree, obj)

    # for a binary operation, we need to merge two existing parts
    if (op in logic.op_list["OPS_BINARY"]):
        left = layouter(tree["left"], obj)
        right = layouter(tree["right"], obj)
        return layout_binary(op, left, right, tree, obj)

    raise Exception("Unexpected operator during rendering")


def layout_const(op, tree, obj):
    doesMatch = logic.matches(tree, obj)
    is_filter = False

    # if it is a filter, include key, value
    if (op in logic.op_list["OPS_FILTERS"]):
        is_filter = True

    return {
        'size': [1, 1],  # height x width
        'mainX': 0,
        'out': logic.matches(tree, obj),
        'grid': [[
            {
                'type': 'node',
                'prop': {
                    'class': 'const',
                    'op': op,

                    'is_filter': is_filter,
                    'key': tree["key"],
                    'value': tree["value"],

                    'input': [],
                    'output': doesMatch
                }
            }
        ]]
    }


def layout_unary(op, right, tree, obj):
    # get some properties from the right.
    rightSize = right['size']
    rightGrid = right['grid']
    rightOut = right['out']
    rightX = right['mainX']

    # check the value we should return
    doesMatch = logic.matches(tree, obj)

    # these are two new lines to render
    nodeline = []
    connline = []

    # create them with a lot of empty space.
    for i in range(rightSize[1]):
        if i != rightX:
            nodeline.append({
                "type": "empty"
            })

            connline.append({
                "type": "empty"
            })
        else:
            # push the node on top
            nodeline.append({
                'type': 'node',
                'prop': {
                    'op': op,
                    'input': [rightOut],
                    'output': doesMatch
                }
            })

            # push a connection line
            connline.append({
                'type': 'conn',
                'prop': {
                    'class': 'tree_connect_ver',
                    'active': [rightOut]
                }
            })

    # add the connection line
    rightGrid.insert(0, connline)

    # and the nodeline
    rightGrid.insert(0, nodeline)

    # and assemble the thing to return
    return {
        'size': [rightSize[0] + 2, right['size'][1]],
        'mainX': rightX,
        'out': doesMatch,
        'grid': rightGrid
    }


def make_empty_line(size):
    return [{"type": "empty"} for i in range(size)]


def layout_binary(op, left, right, tree, obj):
    # get some properties from the left.
    leftSize = left['size']
    leftGrid = left['grid']
    leftOut = left['out']
    leftX = left['mainX']

    # get some properties from the right.
    rightSize = right['size']
    rightGrid = right['grid']
    rightOut = right['out']
    rightX = right['mainX']

    # the new size
    newWidth = leftSize[1] + rightSize[1] + 1
    newHeight = max(leftSize[0], rightSize[0]) + 2

    # check the value we should return
    doesMatch = logic.matches(tree, obj)

    # these are two new lines to render
    nodeline = []
    connline = []

    # create the new top lines
    for i in range(newWidth):
        if (i != leftSize[1]):
            nodeline.append({
                'type': 'empty'
            })

            # for the left x, we need to connect towards the right
            if (i == leftX):
                connline.append({
                    'type': 'conn',
                    'prop': {
                        'active': [leftOut],
                        'class': 'tree_connect_bot_right'
                    }
                })
            elif i < leftX:
                connline.append({
                    'type': 'empty'
                })
            elif (i <= leftSize[1]):
                connline.append({
                    'type': 'conn',
                    'prop': {
                        'active': [leftOut],
                        'class': 'tree_connect_hor'
                    }
                })
            elif (i <= leftSize[1] + rightX):
                connline.append({
                    'type': 'conn',
                    'prop': {
                        'active': [rightOut],
                        'class': 'tree_connect_hor'
                    }
                })
            elif (i == leftSize[1] + rightX + 1):
                connline.append({
                    'type': 'conn',
                    'prop': {
                        'active': [rightOut],
                        'class': 'tree_connect_bot_left'
                    }
                })
            else:
                connline.append({
                    'type': 'empty'
                })
        else:
            # push the node on top
            nodeline.append({
                'type': 'node',
                'prop': {
                    'class': 'binary',
                    'op': op,
                    'input': [leftOut, rightOut],
                    'output': doesMatch
                }
            })

            # push the connection line l / r
            connline.append({
                'type': 'conn',
                'prop': {
                    'active': [leftOut, rightOut],
                    'class': 'tree_connect_top_lr'
                }
            })

    # create a new grid
    newGrid = []

    # push the top two lines
    newGrid.append(nodeline)
    newGrid.append(connline)

    for i in range(newHeight - 2):
        newGrid.append(
            [] +

            (leftGrid[i] if len(leftGrid) > i else make_empty_line(
                leftSize[1])) +

            [{
                "type": "empty"
            }] +

            (rightGrid[i] if len(rightGrid) > i else make_empty_line(
                rightSize[1]))
        )

    # and assemble the thing to return
    return {
        'size': [newHeight, newWidth],
        'mainX': leftSize[1],
        'out': doesMatch,
        'grid': newGrid
    }
