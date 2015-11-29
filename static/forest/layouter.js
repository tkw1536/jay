(function(global){
    var op_list = logic.op_list; 
    
    var layouter = function( tree , obj) {
      var op = tree['op']; 
      var right, left; 
      
      // if we have a constant, it is easy
      if (OP_TRUE.indexOf(op) != -1 || OP_FALSE.indexOf(op) != -1) {
        return layout_const(op, tree, obj);
      }
      
      // if we have a unary, we add two more rows on the top
      if (op_list.OPS_UNARY.indexOf(op) != -1) {
        right = layouter(op['right'], obj); 
        
        return layout_unary(op, right, tree, obj); 
      }
      
      // everything else: LATER
    }
    
    var layout_const = function(op, tree, obj) {
      return {
        'width': 1, 
        'height': 1, 
        'mainX': 0, 
        'grid': [[
          {
            'type': op, 
            'out': logic.matches(tree, obj)
          }
        ]]
      }
    }
    
    var layout_unary = function(op, right, tree, obj) {
      
      
      
      
      return {
        'width': 1, 
        'height': 1, 
        'mainX': [0, 0], 
        'grid': [[
          {
            'type': op, 
            'out': logic.matches(tree, obj)
          }
        ]]
      }
    }
    
    
    // attach to the global window object if available
    global.layouter = layouter;

    if (typeof exports !== 'undefined') {
      if (typeof module !== 'undefined' && module.exports) {
        exports.layouter = module.exports.layouter = layouter;
      } else {
        exports.layouter = layouter;
      }
    }
    
})(this); 