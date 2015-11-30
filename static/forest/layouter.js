(function(global){
    var op_list = logic.op_list;

    var layouter = function( tree , obj) {
      var op = tree['op'];
      var right, left;

      // if we have a constant or a filter, there is only one thing to render.
      if (op_list.OP_TRUE.indexOf(op) != -1 || op_list.OP_FALSE.indexOf(op) != -1 || op_list.OPS_FILTERS.indexOf(op) != -1) {
        return layout_const(op, tree, obj);
      }

      // for a unary operation, we add a new node on top
      if (op_list.OPS_UNARY.indexOf(op) != -1) {
        right = layouter(op['right'], obj);
        return layout_unary(op, right, tree, obj);
      }

      // for a binary operation, we need to merge the two existing parts
      if (op_list.OPS_BINARY.indexOf(op) != -1) {
        left = layouter(op['left'], obj);
        right = layouter(op['right'], obj);
        return layout_binary(op, left, right, tree, obj);
      }
    }

    var layout_const = function(op, tree, obj) {
      var res = logic.matches(tree, obj);

      // TODO: CHECK IF FILTER

      return {
        'size': [1, 1] // height x width
        'mainX': 0,
        'out': logic.matches(tree, obj)
        'grid': [[
          {
            'type': 'node',
            'prop': {
              'op': op,
              'input': [],
              'output': out
            }
          }
        ]]
      };
    }

    var layout_unary = function(op, right, tree, obj) {

      // get some properties from the right.
      var rightSize = right['size'];
      var rightGrid = right['grid'];
      var rightOut = right['out'];
      var rightX = right['mainX'];

      // check the value we should return
      var doesMatch = logic.matches(tree, obj);

      // these are two new lines to render
      var nodeline = [];
      var connline = [];

      // create them with a lot of empty space.
      for (var i = 0; i < rightSize[1]; i++) {
        if (i != rightX) {
          nodeline.push({
            'type': 'empty'
          });

          connline.push({
            'type': 'empty'
          });
        } else {

          // push the node on top
          nodeline.push({
            'type': 'node',
            'prop': {
              'op': op,
              'input': [rightOut],
              'output': doesMatch
            }
          });

          // push a connection line
          connline.push({
            'type': 'conn',
            'prop': {
              'active': [rightOut],
              'class': 'tree_connect_ver'
            }
          })
        }
      }

      // add the connection line
      rightGrid.unshift(connline);

      // and the nodeline
      rightGrid.unshift(nodeline)

      // and assemble the thing to return
      return {
        'size': [rightSize[0]+2, right['size'][1]]
        'mainX': rightX,
        'out': doesMatch,
        'grid': rightGrid
      };
    }

    var layout_binary = function(op, left, right, tree, obj) {

      // get some properties from the right.
      var leftSize = left['size'];
      var leftGrid = left['grid'];
      var leftOut = left['out'];
      var leftX = left['mainX'];

      // get some properties from the right.
      var rightSize = right['size'];
      var rightGrid = right['grid'];
      var rightOut = right['out'];
      var rightX = right['mainX'];

      // the new size
      var newWidth = leftSize[1]+rightSize[1]+1

      // check the value we should return
      var doesMatch = logic.matches(tree, obj);

      // these are two new lines to render
      var nodeline = [];
      var connline = [];

      // create them with a lot of empty space.
      for (var i = 0; i < rightSize[1].length; i++) {
        if (i != rightX) {
          nodeline.push({
            'type': 'empty'
          });

          connline.push({
            'type': 'empty'
          });
        } else {

          // push the node on top
          nodeline.push({
            'type': 'node',
            'prop': {
              'op': op,
              'input': [rightOut],
              'output': doesMatch
            }
          });

          // push a connection line
          connline.push({
            'type': 'conn',
            'prop': {
              'active': [rightOut],
              'class': 'tree_connect_ver'
            }
          })
        }
      }

      // add the connection line
      rightGrid.unshift(connline);

      // and the nodeline
      rightGrid.unshift(nodeline)

      // and assemble the thing to return
      return {
        'size': [rightSize[0]+2, right['size'][1]]
        'mainX': rightX,
        'out': doesMatch,
        'grid': rightGrid
      };
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
