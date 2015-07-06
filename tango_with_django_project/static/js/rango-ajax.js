$(document).ready(function() {
  $('#likes').click(function(){
    var catid;
    catid = $(this).attr("data-catid");
    // this is where we make the AJAX request to out endpoint
    $.get('/rango/like_category/', {category_id: catid}, function(data){
        $('#like_count').html(data);
        $('#likes').hide();
    });
  });
});
