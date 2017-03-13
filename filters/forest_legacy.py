from django.contrib.staticfiles import finders
import os.path
import execjs

from jay.utils import memoize

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

    with open(os.path.join(os.path.dirname(__file__), 'forest.js')) as g:
        src += g.read()

    # and eval them.
    return execjs.compile(src)

# initialise the context
ctx = init()

@memoize
def parse(treestr):
    return ctx.call('parse', treestr)

@memoize
def matches(tree, obj):
    return ctx.call('matches', tree, obj)

def map_match(tree, objs):
    return ctx.call('map_match', tree, objs)

@memoize
def layouter(tree, obj):
    return ctx.call('layouter', tree, obj)

@memoize
def renderer(layout):
    return ctx.call('renderer', layout)

@memoize
def renderer_box(contentNode, inp, out):
    return ctx.call('renderer.box', contentNode, inp, out)

def parse_and_render(treestr, obj):
    tree = parse(treestr)
    layout = layouter(tree, obj)
    return renderer(layout)
