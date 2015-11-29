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


$(function(){/*
  renderFALSE().appendTo("#node_false");
  
  renderTRUE().appendTo("#node_true");
  
  renderNOT(false).appendTo("#node_not_false"); 
  renderNOT(true).appendTo("#node_not_true"); 
  
  renderAND(false, false).appendTo("#node_and_false_false"); 
  renderAND(false, true).appendTo("#node_and_false_true"); 
  renderAND(true, false).appendTo("#node_and_true_false"); 
  renderAND(true, true).appendTo("#node_and_true_true"); 
  
  renderOR(false, false).appendTo("#node_or_false_false"); 
  renderOR(false, true).appendTo("#node_or_false_true"); 
  renderOR(true, false).appendTo("#node_or_true_false"); 
  renderOR(true, true).appendTo("#node_or_true_true"); 
  
  renderNAND(false, false).appendTo("#node_nand_false_false"); 
  renderNAND(false, true).appendTo("#node_nand_false_true"); 
  renderNAND(true, false).appendTo("#node_nand_true_false"); 
  renderNAND(true, true).appendTo("#node_nand_true_true"); 
  
  renderXOR(false, false).appendTo("#node_xor_false_false"); 
  renderXOR(false, true).appendTo("#node_xor_false_true"); 
  renderXOR(true, false).appendTo("#node_xor_true_false"); 
  renderXOR(true, true).appendTo("#node_xor_true_true"); 
  */
})
