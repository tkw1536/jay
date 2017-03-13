from django import template
from filters.forest import logic, layouter, renderer
import json

register = template.Library()


@register.simple_tag(takes_context=False)
def render_full(src, inp):
    # load some json
    obj = json.loads(inp)

    # parse the source code
    tree = logic.parse(src)

    # make a layout with the given object
    layout = layouter.layouter(tree, obj)

    print(layout)

    # and finally render it
    render = renderer.renderer(layout)

    # that is what we return
    return render


@register.simple_tag(takes_context=False)
def render_lbox(name, inp, out):
    box = "<div class='content_box_logical content_box_" + name.upper() + "'><div class='content_box_logic_content'></div></div>"

    inp = list(map(lambda x: x == '1', str(inp)))
    out = (out == '1')

    return renderer.renderBox(box, inp, out)