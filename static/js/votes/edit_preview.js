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

  $("#open_time, #close_time, #public_time").each(function(){
    // find the input
    var $me = $(this);

    // wrap it in an input group.
    var $div = $("<div class='input-group'>");
    $me.wrap($div);

    $me.parent().append(
      $("<span class='input-group-btn'>").append(
        $("<button type='submit' class='btn btn-default' >&nbsp;Now</button>").click(function(e){

          // do not submit the form
          e.preventDefault();

          // get the time that it is now.
          var now = new Date();

          var timestr = "%Y-%m-%d %H:%M:%S";

          timestr = timestr.replace("%Y", now.getFullYear());
          timestr = timestr.replace("%m", ("0" + (now.getUTCMonth() + 1)).slice(-2));
          timestr = timestr.replace("%d", ("0" + now.getUTCDate()).slice(-2));
          timestr = timestr.replace("%H", ("0" + now.getUTCHours()).slice(-2));
          timestr = timestr.replace("%M", ("0" + now.getUTCMinutes()).slice(-2));
          timestr = timestr.replace("%S", ("0" + now.getUTCSeconds()).slice(-2));

          $me.val(timestr);
        })
      )
    )
  })

});
