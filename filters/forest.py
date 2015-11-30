from django.contrib.staticfiles import finders
import execjs

def init():
    """
        Initialises the javascript context
    """

    # find the path to the static files.

    files = [
        'js/forest/jsep.js',
        'js/forest/logic.js',
        'js/forest/layouter.js',
        'js/forest/renderer.js'
    ]

    src = ''

    for f in files:
        with open(finders.find(f)) as g:
            src += g.read()

    # and eval them.
    return execjs.compile(src)

# initialise the context
ctx = init()

def logic_simplify(obj):
    return ctx.call('logic.simplify', obj)

def logic_parse(obj):
    return ctx.call('logic.parse', obj)

def logic_matches(tree, obj):
    return ctx.call('logic.matches', tree, obj)

def layouter(tree, obj):
    return ctx.call('layouter', tree, obj)

def renderer(layout):
    return ctx.call('renderer', layout)

def renderer_box(contentNode, input, output):
    return ctx.call('renderer.box', contentNode, input, output)
