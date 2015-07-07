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

  // add page from search results
  $('.rango-add').click(function(){
    var catid;
    var title;
    var url;

    catid = $(this).attr("data-catid");
    title = $(this).attr("data-title");
    url = $(this).attr("data-url");
    console.log("the url is", url);
    // make the call
    $.get('/rango/auto_add_page/',
          {url:url, category_id: catid, title:title},
          function(data){
            //what do I do here?
            // update the page div
            $('#page').html(data);
            });
  });
});
