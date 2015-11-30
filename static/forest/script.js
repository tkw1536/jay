var boxWidth = 300;
var lineHeight = 20;

// ====================
// RENDER code
// ====================

var renderStatusNode = function(status){
  return $("<div>")
  .addClass("status_node")
  .addClass(status?"status_node_true":"status_node_false");

  return statusNode;
};

var renderBox = function(contentNode, inStatus, outStatus) {

  // make a box to contain all the other items
  var box = $("<div>").addClass("tree_box");

  // render a box for the output
  var outBox = renderStatusNode(outStatus)
  .addClass("status_node_center")
  .appendTo(box);


  // make a central box for the content
  var contentBox = $("<div>")
  .addClass("content_box")
  .appendTo(box)
  .append(contentNode);


  // make two nodes for input / output
  if (inStatus.length === 1){
    renderStatusNode(inStatus[0])
    .addClass("status_node_center")
    .appendTo(box);
  } else if (inStatus.length === 2){
    renderStatusNode(inStatus[0])
    .addClass("status_node_left")
    .appendTo(box);

    renderStatusNode(inStatus[1])
    .addClass("status_node_right")
    .appendTo(box);
  }

  return box;
};

// ====================
// LOGIC nodes
// ====================

var renderTRUE = function(){
  var box = $("<div>")
  .addClass("content_box_logical content_box_TRUE");
  return renderBox(box, [], true);
};

var renderFALSE = function(){
  var box = $("<div>")
  .addClass("content_box_logical content_box_FALSE");
  return renderBox(box, [], false);
};

var renderNOT = function(status){
  var box = $("<div>")
  .addClass("content_box_logical content_box_NOT");
  return renderBox(box, [!!status], !status);
};

var renderAND = function(inA, inB){
  var box = $("<div>")
  .addClass("content_box_logical content_box_AND");
  return renderBox(box, [!!inA, !!inB], inA && inB);
};

var renderOR = function(inA, inB){
  var box = $("<div>")
  .addClass("content_box_logical content_box_OR");
  return renderBox(box, [!!inA, !!inB], inA || inB);
};

var renderNAND = function(inA, inB){
  var box = $("<div>")
  .addClass("content_box_logical content_box_NAND");
  return renderBox(box, [!!inA, !!inB], !(inA && inB));
};

var renderXOR = function(inA, inB){
  var box = $("<div>")
  .addClass("content_box_logical content_box_XOR");
  return renderBox(box, [!!inA, !!inB], (!!inA ^ !!inB));
};

// ====================
// RENDERING A GRID
// ====================
var renderGrid = function (layout) {
  // the grid which contains the actual data
  var grid = layout.grid;

  // dimensions
  var height = layout.size[0];
  var width = layout.size[1];

  var $table = $("<table>");
  var $tr, $td, node, box;

  for(var i = 0; i < height; i++){
    $tr = $("<tr>").appendTo($table);

    for (var j = 0; j < width; j++){
      node = grid[i][j];
      $td = $("<td>").appendTo($tr);

      // if the node is empty, do nothing.
      if (node["type"] === 'empty'){
        /* do nothing */

      // if the node is a connection, draw the right arrows in the right direction
      } else if (node["type"] === 'conn'){

        // for a double connection we need to add two divs
        if(node["prop"]["class"] === "tree_connect_top_lr") {
          $td.append(
            $("<div>").addClass("tree_connect_top_lr_left" + " " + (node["prop"]["active"][0] ? "tree_connect_true" : "tree_connect_false")),
            $("<div>").addClass("tree_connect_top_lr_right" + " " + (node["prop"]["active"][1] ? "tree_connect_true" : "tree_connect_false"))
          )

        // for a single connection we need to add one div
        } else /* if(node["prop"]["class"] === "tree_connect_ver" || node["prop"]["class"] === "tree_connect_hor" || node["prop"]["class"] === "tree_connect_bot_right" || || node["prop"]["class"] === "tree_connect_bot_left") */ {
          $td.append(
            $("<div>").addClass(node["prop"]["class"] + " " + (node["prop"]["active"][0] ? "tree_connect_true" : "tree_connect_false"))
          )
        }
      } else /* if (node["type"] === "node") */ {
        // TODO: Implement filters
        box = $("<div>").addClass("content_box_logical content_box_"+node["prop"]["op"].toUpperCase());
        $td.append(
          renderBox(box, node["prop"]["input"], node["prop"]["output"])
        )
      }

    }
  }

  return $table;
}


$(function(){
  var tree = logic.parse("!(true && false) || false || (false || !(true))");
  var layout = layouter(tree, {});
  console.log(layout.grid);
  renderGrid(layout).appendTo("#test");
})
