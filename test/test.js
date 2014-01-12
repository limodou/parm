$(function(){
    $('.div').on('click', function(e){
        e.preventDefault();
        $.ajax({
            url:'/test',
            dataType:'json',
            success:function(result){
                show_message(result);
            }
        });
    });
});