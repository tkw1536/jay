from django import template
import filters.forest_legacy as forest
import json

register = template.Library()

@register.simple_tag(takes_context=False)
def render_full(src, inp):

    # load some json
    obj = json.loads(inp)

    # parse the source code
    tree = forest.parse(src)

    # make a layout with the given object
    layout = forest.layouter(tree, obj)

    # and finally render it
    render = forest.renderer(layout)

    # that is what we return
    return render


@register.simple_tag(takes_context=False)
def render_lbox(name, inp, out):
    box = "<div class='content_box_logical content_box_"+name.upper()+"'><div class='content_box_logic_content'></div></div>"

    inp = list(map(lambda x:x=='1', str(inp)))
    out = (out == '1')

    return forest.renderer_box(box, inp, out)
