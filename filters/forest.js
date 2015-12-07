
/** Parses a string into a tree */
var parse = function(obj){
  return logic.parse(obj);
};

/** Simplifies a parsed tree */
var simplify = function( tree ){
  return logic.simplify(tree);
};

/** Checks if an object matches a filter tree */
var matches = function(tree, obj){
  return logic.matches(tree, obj);
}

/** Finds objects that match a filter tree */
var map_match = function(tree, objs){
  var res = [];

  for(var i = 0; i < objs.length; i++){
    res.push(matches(tree, objs[i]));
  }

  return res;
}
