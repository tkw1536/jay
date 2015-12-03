$(function(){
  // find all the fields
  var description = $("#description");
  var preview = $("#preview");

  description.on("input propertychange", function(){
    var val = description.val();
    preview.html(markdown.toHTML(val));
  });
});
