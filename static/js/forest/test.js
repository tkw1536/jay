// a very simple test case. 

var logic = require("./logic").logic;
var layouter = require("./layouter").layouter;
var renderer = require("./renderer").renderer;

var tree = logic.parse("(college==Mercator) and (year > 14)");
var obj = {'college': 'Mercator', 'year': 15};

var render = layouter(tree, obj);
var matches = logic.matches(tree, obj);

console.log(matches);
console.log(JSON.stringify(render, null, 4));
