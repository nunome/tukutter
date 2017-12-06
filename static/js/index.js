$(function(){
  $(window).scroll(function() {
    $('ul').toggleClass('fixed', $(this).scrollTop() > 105);
    $('.stream').toggleClass('fixed', $(this).scrollTop() > 105);
  });
});
