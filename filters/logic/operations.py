import json
from . import checker
from . import simplifier
from . import evaluator

def from_json_string(obj):
    """
        Parses a JSON string representing an object.

        obj: Object String to parse
    """

    # try to parse the json
    try:
        jobj = json.loads(obj)
    except Exception as e:
        return None

    # clean it up
    pobj = checker.composite(jobj)

    # if it fails, return none
    if pobj == None:
        return None

    # simplify it
    return simplifier.simplify(pobj)

def json_string(obj):
    """
        Parses, cleans up and returns a json string operation.
    """

    # parse the json string
    fjs = from_json_string(obj)

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
