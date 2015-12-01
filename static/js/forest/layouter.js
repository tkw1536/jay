(function(global){

  // take the global logic variable
  var logic = global.logic;

  // if it is missing, return it.
  if (typeof logic === 'undefined' && typeof require === 'function') {
    logic = require('./logic').logic;
  } else if (typeof logic === 'undefined') {
    throw new Error('The logic module is needed for this parser to work. ');
  }

  var op_list = logic.op_list;

  var layouter = function( tree , obj) {
    var op = tree['operation'];
    var right, left;

    // if we have a constant or a filter, there is only one thing to render.
    if (op_list.OP_TRUE.indexOf(op) != -1 || op_list.OP_FALSE.indexOf(op) != -1 || op_list.OPS_FILTERS.indexOf(op) != -1) {
      return layout_const(op, tree, obj);
    }

    // for a unary operation, we add a new node on top
    if (op_list.OPS_UNARY.indexOf(op) != -1) {
      right = layouter(tree['right'], obj);
      return layout_unary(op, right, tree, obj);
    }

    // for a binary operation, we need to merge the two existing parts
    if (op_list.OPS_BINARY.indexOf(op) != -1) {
      left = layouter(tree['left'], obj);
      right = layouter(tree['right'], obj);
      return layout_binary(op, left, right, tree, obj);
    }
  }

  var layout_const = function(op, tree, obj) {
    var doesMatch = logic.matches(tree, obj);

    var is_filter = false;

    // if it is a filter, include key, value
    if (op_list.OPS_FILTERS.indexOf(op) != -1) {
      is_filter = true;
    }

    return {
      'size': [1, 1], // height x width
      'mainX': 0,
      'out': logic.matches(tree, obj),
      'grid': [[
        {
          'type': 'node',
          'prop': {
            'class': 'const',
            'op': op,

            'is_filter': is_filter, 
            'key': tree.key,
            'value': tree.value,

            'input': [],
            'output': doesMatch
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
            'class': 'unary',
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
      'size': [rightSize[0]+2, right['size'][1]],
      'mainX': rightX,
      'out': doesMatch,
      'grid': rightGrid
    };
  }

  var make_empty_line = function(size){
    var empty = [];

    for(var i = 0; i < size ; i++){
      empty.push({'type': 'empty'})
    }

    return empty;
  }

  var layout_binary = function(op, left, right, tree, obj) {

    // get some properties from the left.
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
    var newHeight = Math.max(leftSize[0], rightSize[0]) + 2;

    // check the value we should return
    var doesMatch = logic.matches(tree, obj);

    // these are two new lines to render
    var nodeline = [];
    var connline = [];

    // create the new top lines
    for (var i = 0; i < newWidth; i++) {
      if (i != leftSize[1]) {
        nodeline.push({
          'type': 'empty'
        });


        // for the left x, we need to connect towards the right
        if (i == leftX){
          connline.push({
            'type': 'conn',
            'prop': {
              'active': [leftOut],
              'class': 'tree_connect_bot_right'
            }
          });
        } else if ( i < leftX){
          connline.push({
            'type': 'empty'
          });
        } else if (i <= leftSize[1]) {
          connline.push({
            'type': 'conn',
            'prop': {
              'active': [leftOut],
              'class': 'tree_connect_hor'
            }
          });
        } else if (i <= leftSize[1] + rightX) {
          connline.push({
            'type': 'conn',
            'prop': {
              'active': [rightOut],
              'class': 'tree_connect_hor'
            }
          });
        } else if (i == leftSize[1] + rightX + 1) {
          connline.push({
            'type': 'conn',
            'prop': {
              'active': [rightOut],
              'class': 'tree_connect_bot_left'
            }
          });
        } else {
          connline.push({
            'type': 'empty'
          });
        }
      } else {

        // push the node on top
        nodeline.push({
          'type': 'node',
          'prop': {
            'class': 'binary',
            'op': op,
            'input': [leftOut, rightOut],
            'output': doesMatch
          }
        });

        // pish the connection line l / r
        connline.push({
          'type': 'conn',
          'prop': {
            'active': [leftOut, rightOut],
            'class': 'tree_connect_top_lr'
          }
        });
      }
    }

    // create a new grid
    var newGrid = [];

    // push the top two lines
    newGrid.push(nodeline);
    newGrid.push(connline);

    for(var i = 0; i < newHeight - 2; i++ ){
      newGrid.push(
        []
        .concat(
          leftGrid.length > i ? leftGrid[i] : make_empty_line(leftSize[1])
        )
        .concat([{
          'type': 'empty'
        }])
        .concat(
          rightGrid.length > i ? rightGrid[i] : make_empty_line(rightSize[1])
        )
      );
    }

    // and assemble the thing to return
    return {
      'size': [newHeight, newWidth],
      'mainX': leftSize[1],
      'out': doesMatch,
      'grid': newGrid
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
