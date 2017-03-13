import re


def htmlescape(s):
    return s.replace(r"&", '&amp;').replace("<", "&lt;").replace(">", "&gy;")


def classescape(cls):
    return re.sub(r"\s", "_", cls).upper()


def renderer(layout):
    # the grid which contains the actual data
    grid = layout["grid"]

    # dimensions
    height = layout["size"][0]
    width = layout["size"][1]

    table = "<table>"

    for i in range(height):
        tr = "<tr>"

        for j in range(width):
            node = grid[i][j]
            td = "<td>"

            # if the node is empty, do nothing.
            if node["type"] == "empty":
                pass

            # if the node is a connection, draw the right arrows in the right direction
            elif node["type"] == "conn":

                # for a double connection we need to add two divs
                if node["prop"]["class"] == "tree_connect_top_lr":
                    td += "<div class='tree_connect_top_lr_left " + (
                        "tree_connect_true" if node["prop"]["active"][
                            0] else "tree_connect_false") + "'></div>";
                    td += "<div class='tree_connect_top_lr_right " + (
                        "tree_connect_true" if node["prop"]["active"][
                            1] else "tree_connect_false") + "'></div>";
                # for a single connection we need to add one div
                else:
                    td += "<div class='" + node["prop"]["class"] + " " + (
                        "tree_connect_true" if node["prop"]["active"][
                            0] else "tree_connect_false") + "'></div>";
            else:
                if "is_filter" in node["prop"] and node["prop"]["is_filter"]:
                    key = htmlescape(node["prop"]["key"])
                    value = htmlescape(node["prop"]["value"])

                    box = """<div class='content_box_filter content_box_{}'>
                        <div class='content_box_filter_key'>{}</div>
                        <div class='content_box_filter_content'></div>
                        <div class='content_box_filter_value'>{}</div>
                    </div>
                    """.format(classescape(node["prop"]["op"]), key, value)
                else:
                    box = """<div class='content_box_logical content_box_{}'>
                        <div class='content_box_logic_content'></div>
                    </div>
                    """.format(classescape(node["prop"]["op"]))

                td += renderBox(box, node["prop"]["input"],
                                node["prop"]["output"])

            # close the cell and add it to the row
            td += "</td>"
            tr += td

        # close the table row and add it to the table
        tr += "</tr>"
        table += tr

    # close the table
    table += "</table>"
    return table


def renderStatusNode(addClass, status):
    return "<div class='status_node " + \
           addClass + " " + \
           ("status_node_true" if status else "status_node_false") + \
           "'></div>"


def renderBox(contentNode, inStatus, outStatus):
    # make a box to contain all the other items
    box = "<div class='tree_box'>"

    # render a box for the output
    box += renderStatusNode("status_node_center", outStatus)

    # make a central box for the content
    box += "<div class='content_box'>" + contentNode + "</div>"

    # make two nodes for input / output
    if (len(inStatus) == 1):
        box += renderStatusNode("status_node_center", inStatus[0])
    elif (len(inStatus) == 2):
        box += renderStatusNode("status_node_left", inStatus[0])
        box += renderStatusNode("status_node_right", inStatus[1])

    # close the box
    box += "</div>"

    # and return it.
    return box
