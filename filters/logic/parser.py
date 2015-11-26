import os

from django.contrib.staticfiles import finders

import execjs

def init():
    """
        Initialises the javascript context
    """

    # find the path to the static files.
    DJANGO_JSEP_PATH = finders.find('js/parser/jsep.js')
    DJANGO_PARSER_PATH = finders.find('js/parser/parser.js')

    # read the files
    with open(DJANGO_JSEP_PATH) as f:
        jsep_source = f.read()

    with open(DJANGO_PARSER_PATH) as g:
        parser_source = g.read()

    # and eval them.
    return execjs.compile(jsep_source + parser_source)

# create the context
ctx = init()

def parse(data):
    """
        Compiles a string.
    """
    return ctx.call("parse", str(data))
