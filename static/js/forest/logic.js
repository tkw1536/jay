(function (global) {
  // =============================================================================
  // OPERATOR NAMES CONFIG
  // =============================================================================
  var OP_TRUE             =  [ 'true' ];
  var OP_FALSE            =  [ 'false' ];

  var OP_NOT              =  [ 'not', '!' ];

  var OP_EQUALS           =  [ 'equals', '=', '==', '===' ];

  var OP_LESS             =  [ 'less than', '<' ];
  var OP_LESS_EQUAL       =  [ 'less than or equal', '<=', '=<', ];

  var OP_GREATER          =  [ 'greater than', '>' ];
  var OP_GREATER_EQUAL    =  [ 'greater than or equal', '>=', '=>' ];

  var OP_CONTAINS         =  [ 'contains' , '::' ];

  var OP_MATCHES          =  [ 'matches' , 'unicorn' , '@' ];

  var OP_AND              =  [ 'and' , '&', '&&' , '*'];

  var OP_OR               =  [ 'or', '|', '||', '+'];

  var OP_NAND             =  [ 'nand', '!&' ];

  var OP_XOR              =  [ 'xor', '^' ];

  // =============================================================================
  // OPERATOR GROUPS CONFIG
  // =============================================================================

  var OPS_UNARY     = [] // unary operators that expect one binary argument
                      .concat(OP_NOT)

  var OPS_FILTERS   = [] // filters that expect a key and value argument
                      .concat(OP_EQUALS)
                      .concat(OP_LESS)
                      .concat(OP_LESS_EQUAL)
                      .concat(OP_GREATER)
                      .concat(OP_GREATER_EQUAL)
                      .concat(OP_CONTAINS)
                      .concat(OP_MATCHES);

  var OPS_BINARY    = [] // binary operators that expect to logical arguments
                      .concat(OP_AND)
                      .concat(OP_OR)
                      .concat(OP_NAND)
                      .concat(OP_XOR);

  // =============================================================================

  var clean_jsep = function (jsep) {
    // operators to remove
    var unary_operators_before  = [ '-', '!', '~', '+' ];
    var binary_operators_before = [ '||', '&&', '|', '^', '&', '==', '!=', '===', '!==', '<', '>', '<=',  '>=', '<<', '>>', '>>>', '+', '-', '*', '/', '%' ];

    // iterator variables
    var i, _l;

    // remove the unary operators
    _l = unary_operators_before.length;
    for ( i = 0 ; i < _l ; i++ ) {
        jsep.removeUnaryOp(unary_operators_before[i]);
    }

    // remove all the binary operators
    _l = binary_operators_before.length;
    for ( i = 0 ; i < _l ; i++ ) {
        jsep.removeBinaryOp(binary_operators_before[i]);
    }

    // return it
    return jsep;
  }

  var popu_jsep = function (jsep) {
    // iterator variables
    var i, _l;

    // add the unary operators
    _l = OPS_UNARY.length;
    for ( i = 0 ; i < _l ; i++ ) {
        jsep.addUnaryOp(OPS_UNARY[i]);
    }

    // add the binary operators
    _l = OPS_BINARY.length;
    for ( i = 0 ; i < _l ; i++ ) {
        jsep.addBinaryOp(OPS_BINARY[i], 1);
    }

    // add the binary filters
    _l = OPS_FILTERS.length;
    for ( i = 0 ; i < _l ; i++ ) {
        jsep.addBinaryOp(OPS_FILTERS[i], 2);
    }

    return jsep;
  }

  // try and take the global jsep
  var jsep = global.jsep;

  // if jsep is not available, try to load it.
  if (typeof jsep === 'undefined' && typeof require === 'function') {
    jsep = require('./jsep').jsep;
  } else if (typeof jsep === 'undefined') {
    throw new Error('jsep <http://jsep.from.so/> is needed for this parser to work. ');
  }

  // load jsep and set properties
  jsep = clean_jsep(jsep);
  jsep = popu_jsep(jsep);

  var parse_binary = function ( tree ) {

    /*
      A binary expression is either:

      1. A literal expression
        1a. the literal true  ( ===> true )
        1b. the literal false ( ===> false )
        1c. the literal null ( ===> false )
      2. A unary logical expression
        2a. a not expression
      3. A binary logical connetive
        3a. a logical And
        3b. a logical or
        3c. a logical nand
        3d. a logical xor
      4. A binary filter
        4a. an equals filter
        4b. a less filter
        4c. a less or equals filter
        4d. a greater filter
        4e. a greater than filter
        4f. a contains filter
        4g. a matches filter
      5. A primitive expression ( ==> is the string false-ish ? )
    */

    var i;

    // if there is nothing, return
    if ( !tree ) {
      throw new Error('Missing binary expression. ');
    }

    // check for literals
    if (tree.type === 'Literal') {
      if (tree.raw === OP_TRUE[0]){
        return {'operation': OP_TRUE[0]};
      } else if (tree.raw === OP_FALSE[0]){
        return {'operation': OP_FALSE[0]};
      } else if (tree.raw === 'null'){
        return {'operation': OP_FALSE[0]};
      }
    }

    // check for a unary expression
    if (tree.type === 'UnaryExpression') {

      // find the index inside the logical not
      i = OP_NOT.indexOf(tree.operator);


      if (i != -1 ){
        return {'operation': OP_NOT[0], 'right': parse_binary(tree.argument)};
      } else {
        throw new Error('Expected a binary expression, but found unknown UnaryExpression type in input. ');
      }

    }

    // check for binary logical connectives
    if (tree.type === 'BinaryExpression' || tree.type === 'LogicalExpression') {

      // check for a logical and
      i = OP_AND.indexOf(tree.operator);
      if (i != -1) {
        return {'operation': OP_AND[0], 'left': parse_binary(tree.left), 'right': parse_binary(tree.right)};
      }

      // check for a logical or
      i = OP_OR.indexOf(tree.operator);
      if (i != -1) {
        return {'operation': OP_OR[0], 'left': parse_binary(tree.left), 'right': parse_binary(tree.right)};
      }

      // check for a logical nand
      i = OP_NAND.indexOf(tree.operator);
      if (i != -1) {
        return {'operation': OP_NAND[0], 'left': parse_binary(tree.left), 'right': parse_binary(tree.right)};
      }

      // check for a logical xor
      i = OP_XOR.indexOf(tree.operator);
      if (i != -1) {
        return {'operation': OP_XOR[0], 'left': parse_binary(tree.left), 'right': parse_binary(tree.right)};
      }

    }

    // check for binary filter
    if (tree.type === 'BinaryExpression' || tree.type === 'LogicalExpression') {

      // an equals filter
      i = OP_EQUALS.indexOf(tree.operator);
      if (i != -1) {
        return {'operation': OP_EQUALS[0], 'key': parse_primitive(tree.left), 'value': parse_primitive(tree.right)};
      }

      // a less filter
      i = OP_LESS.indexOf(tree.operator);
      if (i != -1) {
        return {'operation': OP_LESS[0], 'key': parse_primitive(tree.left), 'value': parse_primitive(tree.right)};
      }

      // a less or equals filter
      i = OP_LESS_EQUAL.indexOf(tree.operator);
      if (i != -1) {
        return {'operation': OP_LESS_EQUAL[0], 'key': parse_primitive(tree.left), 'value': parse_primitive(tree.right)};
      }

      // a greater filter
      i = OP_GREATER.indexOf(tree.operator);
      if (i != -1) {
        return {'operation': OP_GREATER[0], 'key': parse_primitive(tree.left), 'value': parse_primitive(tree.right)};
      }

      // a greater or equals filter
      i = OP_GREATER_EQUAL.indexOf(tree.operator);
      if (i != -1) {
        return {'operation': OP_GREATER_EQUAL[0], 'key': parse_primitive(tree.left), 'value': parse_primitive(tree.right)};
      }

      // a contains filter
      i = OP_CONTAINS.indexOf(tree.operator);
      if (i != -1) {
        return {'operation': OP_CONTAINS[0], 'key': parse_primitive(tree.left), 'value': parse_primitive(tree.right)};
      }

      // a matches filter
      i = OP_MATCHES.indexOf(tree.operator);
      if (i != -1) {
        return {'operation': OP_MATCHES[0], 'key': parse_primitive(tree.left), 'value': parse_primitive(tree.right)};
      }

      throw new Error('Expected a binary expression, but found unknown BinaryExpression / LogicalExpression in input. ');
    }

    var is_primitive = false;

    // check if we have a primitive expression.
    try {
      parse_primitive(tree);
      is_primitive = true;
    } catch (e){}

    if (is_primitive) {
      throw new Error('Expected a binary expression, but found a primitive instead. ');
    } else {
      throw new Error('Expected a binary expression, but found unknown expression type in input. ');
    }
  }

  var parse_primitive = function ( tree ) {
    /*
      A primitive expression is either:

      1. A ThisExpression ( ==> this )
      1. A literal expression ( ==> literal.raw )
      2. A identifier expression ( ==> identifier.name )
      3. A non-empty compound expression consisting of primitives as above ( ==> join as strings )
    */

    var i, s, _l;

    // if there is nothing, return
    if ( !tree ) {
      throw new Error('Missing binary expression. ');
    }

    // check for a thisexpression
    if (tree.type === 'ThisExpression') {
      return 'this';
    }

    // check for a literal expression
    if (tree.type === 'Literal') {
      if (typeof tree.value === 'string'){
        return tree.value;
      } else {
        return tree.raw;
      }
    }

    // check for an identifier
    if (tree.type === 'Identifier') {
      return tree.name;
    }

    // in case of a compound expression
    if (tree.type === 'CompoundExpression') {
      s  = [];

      // iterate through the body
      i  = 0;
      _l = tree.body.length;
      for ( i = 0 ; i < _l ; i++ ) {
        s.push(parse_primitive(tree.body[i]));
      }

      // and return a number of joined strings
      return s.join(" ");
    }

    throw new Error('Expected a primitive expression, but found unknown expression type in input. ');
  }


  // remove all the binary expresions
  var parse = function (s) {

    // parse into an abstract syntax tree
    var ast = jsep(s);

    // make this a binary ast
    return parse_binary(ast);
  };

  // simplifies a boolean expression.
  var simplify = function (obj) {

    var left, left_op;
    var right, right_op;

    if (obj['operation'] == OP_AND[0]) {
      // simplifiy on the left and on the right
      left  = simplify(obj['left']);
      right = simplify(obj['right']);

      // find left and right operations
      left_op = left['operation'];
      right_op = right['operation'];

      // if the right operation is a constant
      if (right_op == OP_TRUE[0]){
        return left;
      }

      if (right_op == OP_FALSE[0]){
        return {'operation': OP_FALSE[0]};
      }

      if (left_op == OP_TRUE[0]){
        return right;
      }

      if (left_op == OP_FALSE[0]){
        return {'operation': OP_FALSE[0]};
      }

      // else return the cleaned operation
      return {'operation': OP_AND[0], 'left': left, 'right': right}
    }

    if(obj['operation'] == OP_NAND[0]){
        // simplify on the left and on the right
        left  = simplify(obj['left']);
        right = simplify(obj['right']);

        // find left and right operations
        left_op = left['operation'];
        right_op = right['operation'];

        // if the right operation is a constant
        if(right_op == OP_TRUE[0]){
          return simplify({
              operation: OP_NOT[0],
              'right': left
          });
        }

        if(right_op == OP_FALSE[0]){
          return {'operation': OP_TRUE[0]};
        }


        // if the left operation is a constant
        if (left_op == OP_TRUE[0]){
          return simplify({
              operation: OP_NOT[0],
              'right': right
          });
        }

        if(left_op == OP_FALSE[0]){
          return {'operation': OP_TRUE[0]};
        }

        // else return the cleaned operation
        return {'operation': OP_NAND[0], 'left': left, 'right': right}
      }


      if(obj['operation'] == OP_OR[0]){
        // simplify on the left and on the right
        left  = simplify(obj['left']);
        right = simplify(obj['right']);

        // find left and right operations
        left_op = left['operation'];
        right_op = right['operation'];

        // if the right operation is a constant
        if(right_op == OP_TRUE[0]){
          return {'operation': OP_TRUE[0]};
        }

        if(right_op == OP_FALSE[0]){
          return left;
        }


        // if the left operation is a constant
        if(left_op == OP_TRUE[0]){
          return {'operation': OP_TRUE[0]};
        }

        if(left_op == OP_FALSE[0]){
          return right;
        }


        // else return the cleaned operation
        return {'operation': OP_OR[0], 'left': left, 'right': right};
      }

      if(obj['operation'] == OP_XOR[0]){

        // simplify on the left and on the right
        left  = simplify(obj['left']);
        right = simplify(obj['right']);

        // find left and right operations
        left_op = left['operation'];
        right_op = right['operation'];

        // if the right operation is a constant
        if(right_op == OP_TRUE[0]){
          return simplify({
              'operation': OP_NOT[0],
              'right': left
          });
        }

        if(right_op == OP_FALSE[0]){
          return left;
        }


        // if the left operation is a constant
        if (left_op == OP_TRUE[0]) {
          return simplify({
              'operation': OP_NOT[0],
              'right': right
          });
        }

        if (left_op == OP_FALSE[0]) {
          return right;
        }

        // else return the cleaned operation
        return {'operation': OP_XOR[0], 'left': left, 'right': right};
      }

      if(obj['operation'] == OP_NOT[0]) {
        // simplify the sub operation
        right = simplify(obj['right']);

        // find the operation on the right
        right_op = right['operation'];

        // remove true / false
        if(right_op == OP_TRUE[0]) {
          return {'operation': OP_FALSE[0]};
        }

        if(right_op == OP_FALSE[0]) {
          return {'operation': OP_TRUE[0]};
        }

        // remove double nots
        if(right_op == OP_NOT[0]){
          return simplify(right['right']);
        }

        // ! nand => and
        if( right_op == OP_NAND[0]){
          return {
              'operation': OP_AND[0],
              'left': right['left'],
              'right': right['right']
          };
        };

        // ! and => nand
        if(right_op == OP_AND[0]){
          return {
              'operation': OP_NAND[0],
              'left': right['left'],
              'right': right['right']
          };
        }

        // ! or(a, b) = and(!a, !b)
        if (right_op == OP_OR[0]){
          return {
            'operation': OP_AND[0],
            'left': simplify({operation:OP_NOT[0], right: right['left']}),
            'right': simplify({operation:OP_NOT[0], right: right['right']}),
          }
        }

        return {'operation': OP_NOT[0], 'right': simplify(obj['right'])}
      }
      // otherwise it is a filter, so return as is.
      return obj
  };

  var matches_logical = function (tree, obj) {

    // operation of the tree
    var op = tree['operation'];

    // constants
    if (op === OP_TRUE[0]) {
      return true;
    }

    if (op === OP_FALSE[0]) {
      return false;
    }

    // not
    if (op === OP_NOT[0]) {
      return ! matches_logical(tree['right'], obj);
    }

    // binary operations

    if(op === OP_AND[0]) {
      return matches_logical(tree['left'], obj) && matches_logical(tree['right'], obj);
    }

    if(op === OP_NAND[0]) {
      return ! (matches_logical(tree['left'], obj) && matches_logical(tree['right'], obj));
    }

    if(op === OP_OR[0]) {
      return matches_logical(tree['left'], obj) || matches_logical(tree['right'], obj);
    }

    if(op === OP_XOR[0]) {
      return matches_logical(tree['left'], obj) != matches_logical(tree['right'], obj);
    }

    return matches_filter(tree, obj);
  }

  var match_toString = function (obj) {
    return ''+obj;
  }

  var match_toFloat = function (obj) {
    try {
      return parseFloat(obj)
    } catch(e){
      return parseFloat(match_toString(obj));
    }
  }

  // check if a tree matches a filter
  var matches_filter = function (tree, obj) {

    // find the operation.
    var op = tree['operation'];

    // find the key and value to check.
    var key = tree['key'];
    var value = tree['value'];

    // if the object does not have the property, we can exit immediatly
    if( !obj.hasOwnProperty(key) ) {
      return false;
    }

    // read the key from the object
    var obj_value = obj[key];

    // equality: check if the objects are equal as strings.
    if (op == OP_EQUALS[0]) {
      return match_toString(obj_value) == match_toString(value);
    }

    // numeric comparisions
    if (op == OP_LESS[0]) {
      try{
        value = match_toFloat(value);
        obj_value = match_toFloat(obj_value);
      } catch(e){
        return false;
      }

      return obj_value < value;
    }

    if (op == OP_LESS_EQUAL[0]) {
      try{
        value = match_toFloat(value);
        obj_value = match_toFloat(obj_value);
      } catch(e){
        return false;
      }

      return obj_value <= value;
    }

    if (op == OP_GREATER[0]) {
      try{
        value = match_toFloat(value);
        obj_value = match_toFloat(obj_value);
      } catch(e){
        return false;
      }

      return obj_value > value;
    }

    if (op == OP_GREATER_EQUAL[0]) {
      try{
        value = match_toFloat(value);
        obj_value = match_toFloat(obj_value);
      } catch(e){
        return false;
      }

      return obj_value >= value;
    }


    // check if we match a regular expression
    if (op == OP_MATCHES[0]) {
      try {
        value = new RegExp(value);
      } catch(e) {
        return false;
      }

      // check if it matches the regular expression
      return !!match_toString(obj_value).match(value);
    }

    // check if a value is contained in this array
    if (op == OP_CONTAINS[0] && Array.isArray(obj_value)) {
      return obj_value.indexOf(value) != -1;
    } else if (op == OP_CONTAINS[0]) {
      return match_toString(obj_value).indexOf(value) != -1;
    }

    // ??? what is this?
    return false;
  }

  // check if tree matches an object
  var matches = function( tree, obj ){
    return matches_logical(tree, obj);
  }


  // exports the entire thing in a namespace
  var logic = {
    'parse': parse,
    'simplify': simplify,
    'matches': matches,

    'op_list': {
      'OP_TRUE': OP_TRUE,
      'OP_FALSE': OP_FALSE,

      'OP_NOT': OP_NOT,

      'OP_EQUALS': OP_EQUALS,

      'OP_LESS': OP_LESS,
      'OP_LESS_EQUAL': OP_LESS_EQUAL,

      'OP_GREATER': OP_GREATER,
      'OP_GREATER_EQUAL': OP_GREATER_EQUAL,

      'OP_CONTAINS': OP_CONTAINS,

      'OP_MATCHES': OP_MATCHES,

      'OP_AND': OP_AND,

      'OP_OR': OP_OR,

      'OP_NAND': OP_NAND,

      'OP_XOR': OP_XOR,


      'OPS_UNARY': OPS_UNARY,
      'OPS_FILTERS': OPS_FILTERS,
      'OPS_BINARY': OPS_BINARY
    }
  }



  // attach to the global window object if available
  global.logic = logic;

  if (typeof exports !== 'undefined') {
    if (typeof module !== 'undefined' && module.exports) {
      exports.logic = module.exports.logic = logic;
    } else {
      exports.logic = logic;
    }
  }

})(this);
