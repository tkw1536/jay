$(function(){

  // find all the elements
  var $obj = $("#obj");
  var preview = $("#preview");
  var form = $obj.parents("form");

  // parse the tree
  var tree = JSON.parse($("#filter_tree").val());

  // do something when changing
  $obj.on("input propertychange", function(){
    var obj = $obj.val();

    try{

      // parse it into json
      var jobj = JSON.parse(obj);

      // make a layout and render it
      var layout = layouter(tree, jobj);
      var render = renderer(layout);

      // now actually render it
      preview.html(render);
    } catch(e){
    }
  });

  form.on("submit", function(e){

    // do not submit to save on the server side
    e.preventDefault();

    // update input
    $obj.trigger("input");

    return false;
  });
});
