$(function(){
  // find all the fields
  var description = $("#description");
  var preview = $("#preview");

  description.on("input propertychange", function(){
    var val = description.val();
    preview.html(markdown.toHTML(val));
  });
  
  // HACK: Get the maximal number of votes
  var num_votes = parseInt($("#max_votes").attr("max")); 
  
  // preview for all the options
  for (var i = 0; i < num_votes; i++){
    (function(){
      var description = $("#opt_desc_"+i);
      var preview = $("#opt_preview_"+i);
      
      description.on("input propertychange", function(){
        var val = description.val();
        preview.html(markdown.toHTML(val));
      });
    })(); 
  }
});
