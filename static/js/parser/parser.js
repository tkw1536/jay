(function (global) {
  // =============================================================================
  // OPERATOR NAMES CONFIG
  // =============================================================================
  var OP_NOT              =  [ 'not', '!' ];

  var OP_EQUALS           =  [ 'equals', '=', '==', '===' ];

  var OP_LESS             =  [ 'less then', '<' ];
  var OP_LESS_EQUAL       =  [ 'less then or equal', '<=', '=<', ];

  var OP_GREATER          =  [ 'greater then', '>' ];
  var OP_GREATER_EQUAL    =  [ 'greater then or equal', '>=', '=>' ];

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
    jsep = require('./jsep');
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
        4e. a greater then filter
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
      if (tree.raw === 'true'){
        return {'operation': 'true'};
      } else if (tree.raw === 'false'){
        return {'operation': 'false'};
      } else if (tree.raw === 'null'){
        return {'operation': 'false'};
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


  // attach to the global window object if available
  if (typeof exports === 'undefined') {
    global.parse = parse;
  } else {
    if (typeof module !== 'undefined' && module.exports) {
      exports.parse = module.exports.parse = parse;
    } else {
      exports.parse = parse;
    }

    global.parse = parse; 
  }

})(this);
