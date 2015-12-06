$(function(){
  // find all the fields
  var value = $("#value");
  var submit = $("#submit");
  var preview = $("#preview");
  var error = $("#error");

  // do something whenever it changes
  value.on("keyup", function(){

    // get the value
    var val = value.val();

    try{

      // render the previewed tree
      var tree = logic.parse(val);
      var layout = layouter(tree, {});
      var render = renderer(layout);

      // and show it as html
      preview.html(render);

      // remove the disabled attribute if that worked
      submit.removeAttr("disabled");

      // and clear the error message
      error.empty();
    } catch(e){

      // show the error message
      error.empty().append(
        $("<div>")
        .addClass("alert alert-danger")
        .text(e.message)
        .prepend(
          $("<strong>").text("Error parsing filter")
        )
      );

      // if this failed, do not submit
      submit.attr("disabled", "disabled");
    }
  });
});
