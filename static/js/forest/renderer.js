(function(global){

  var htmlescape = function(str){
    return str.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
  }
  var classescape = function(cls){
    return cls.replace(/\s/, '_').toUpperCase();
  }

  var renderer = function (layout) {
    // the grid which contains the actual data
    var grid = layout.grid;

    // dimensions
    var height = layout.size[0];
    var width = layout.size[1];

    var $table = "<table>";
    var $tr, $td, node, box, key, value;

    for(var i = 0; i < height; i++){
      $tr = "<tr>";

      for (var j = 0; j < width; j++){
        node = grid[i][j];
        $td = "<td>";

        // if the node is empty, do nothing.
        if (node["type"] === 'empty'){
          /* do nothing */

        // if the node is a connection, draw the right arrows in the right direction
        } else if (node["type"] === 'conn'){

          // for a double connection we need to add two divs
          if(node["prop"]["class"] === "tree_connect_top_lr") {
            $td += "<div class='tree_connect_top_lr_left " + (node["prop"]["active"][0] ? "tree_connect_true" : "tree_connect_false")+"'></div>";
            $td += "<div class='tree_connect_top_lr_right " + (node["prop"]["active"][1] ? "tree_connect_true" : "tree_connect_false")+"'></div>";
          // for a single connection we need to add one div
          } else {
            $td += "<div class='"+node["prop"]["class"] + " " + (node["prop"]["active"][0] ? "tree_connect_true" : "tree_connect_false")+"'></div>";
          }
        } else {

          if (node["prop"]["is_filter"]){
            key = htmlescape(node["prop"]["key"])
            value = htmlescape(node["prop"]["value"])

            box = "<div class='content_box_filter content_box_"+classescape(node["prop"]["op"])+"'>" +
            "<div class='content_box_filter_key'>" + key + "</div>" +
            "<div class='content_box_filter_content'></div>" +
            "<div class='content_box_filter_value'>" + value + "</div>" +
            "</div>";
          } else {
            box = "<div class='content_box_logical content_box_"+classescape(node["prop"]["op"])+"'>" +
            "<div class='content_box_logic_content'></div>" + 
            "</div>";
          }

          $td += renderBox(box, node["prop"]["input"], node["prop"]["output"]);
        }

        // close the cell and add it to the row
        $td += "</td>"
        $tr += $td;
      }

      // close the table row and add it to the table
      $tr += "</tr>";
      $table += $tr;
    }

    // close the table
    $table += "</table>";

    return $table;
  }

  var renderStatusNode = renderer.statusNode = function(addClass, status){
    return "<div class='status_node " +
      addClass + " " +
      (status?"status_node_true":"status_node_false") +
      "'></div>";
  };

  var renderBox = renderer.box = function(contentNode, inStatus, outStatus) {

    // make a box to contain all the other items
    var box = "<div class='tree_box'>" +

    // render a box for the output
    renderStatusNode("status_node_center", outStatus) +

    // make a central box for the content
    "<div class='content_box'>" + contentNode + "</div>";

    // make two nodes for input / output
    if (inStatus.length === 1){
      box += renderStatusNode("status_node_center", inStatus[0]);
    } else if (inStatus.length === 2){
      box += renderStatusNode("status_node_left", inStatus[0]);
      box += renderStatusNode("status_node_right", inStatus[1]);
    }

    // close the box
    box += "</div>";

    // and return it.
    return box;
  };

  // attach to the global window object if available
  global.renderer = renderer;

  if (typeof exports !== 'undefined') {
    if (typeof module !== 'undefined' && module.exports) {
      exports.renderer = module.exports.renderer = renderer;
    } else {
      exports.renderer = renderer;
    }
  }
})(this);
