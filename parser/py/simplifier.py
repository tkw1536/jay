def simplify_operation(obj):
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
        right = simplify_operation(obj['right']['right'])

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
