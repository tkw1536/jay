import json
from . import checker
from . import simplifier
from . import evaluator
from . import parser

def from_string(obj):
    """
        Parses a string representing an object.

        obj: Object String to parse
    """

    # try to parse the json
    try:
        jobj = parser.parse(obj)
    except Exception as e:
        print(e)
        return None

    # clean it up
    pobj = checker.composite(jobj)

    # if it fails, return none
    if pobj == None:
        return None

    # simplify it
    return simplifier.simplify(pobj)

def string(obj):
    """
        Parses, cleans up and returns a string operation.
    """

    # parse the string
    fjs = from_string(obj)

    # if that failed, return
    if fjs == None:
        return None

    # else return it as a json string again.
    return json.dumps(fjs)

def evaluate_tree(tree, obj):
    """
        Evaluates a tree object and checks if it matches a given object.
    """

    try:
        return evaluator.composite(json.loads(tree), obj)
    except:
        return None
