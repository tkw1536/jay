from django.contrib.staticfiles import finders
import execjs

def init():
    """
        Initialises the javascript context
    """

    # find the path to the static files.
    DJANGO_JSEP_PATH = finders.find('js/parser/jsep.js')
    DJANGO_LOGIC_PATH = finders.find('js/parser/logic.js')

    # read the files
    with open(DJANGO_JSEP_PATH) as f:
        jsep_source = f.read()

    with open(DJANGO_LOGIC_PATH) as g:
        logic_source = g.read()

    # and eval them.
    return execjs.compile(jsep_source + logic_source)

# initialise the context
ctx = init()

def simplify(obj):
    return ctx.call('logic.simplify', obj)

def parse(obj):
    return ctx.call('logic.parse', obj)

def matches(tree, obj):
    return ctx.call('logic.matches', tree, obj)
