$(document).ready(function() {
  $('#likes').click(function(){
    var catid;
    catid = $(this).attr("data-catid");
    // this is where we make the AJAX request to out endpoint
    $.get('/rango/like_category/',
          // submitted data
          {category_id: catid}, 
          // success handler 
          function(data){
            $('#like_count').html(data);
            $('#likes').hide();
    });
  });

  $('#suggestion').keyup(function(){
    var query; 
    query = $(this).val();
    $.get('/rango/suggest_category/', {suggestion: query}, function(data){
      $('#cats').html(data);
    });
  });
});
