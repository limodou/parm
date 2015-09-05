function viewport()
{
    var e = window, a = 'inner';
    if ( !( 'innerWidth' in window ) )
    {
        a = 'client';
        e = document.documentElement || document.body;
    }
    return { width : e[ a+'Width' ] , height : e[ a+'Height' ] }
}

$(function(){

    // make code pretty
    window.prettyPrint && prettyPrint()

    function setup_toc(){
        var toc = $('#toc');
        if (toc.size() > 0)
        {
            toc.toc({
                'selectors': 'h2,h3', //elements to use as headings
                'highlightOffset': 0, //offset to trigger the next headline
                'offset': 0
            });
            var h = viewport().height - $('#toc').offset()['top'] - 40;
            if (h < toc.height())
                toc.height(h);
            toc.stick_in_parent();
        }
    }
    
    setup_toc();
    
    $(window).resize(function(){
        setup_toc();
    });
     
    //add code comment process
    $('pre, .inline-tag').code_comment();
    
    //process keypress
    $(document).bind('keydown.left', function(){
        var el = $('a[prev-chapter]');
        if (el.length>0){
            el[0].click();
        }
    }).bind('keydown.right', function(){
        var el = $('a[next-chapter]');
        if (el.length>0){
            el[0].click();
        }
    }).bind('keydown.return', function(){
        $('.expander').click();
    }).bind('keydown.h', function(){
        window.location.href = relpath+'/index.html';
    });
    
    //process expander
    $('.expander').click({'opened':false}, function(e){
        if (!e.data.opened){
            $('#article').removeClass('span9').addClass('span12');
            $('#topic').hide().appendTo($('#article'));
            e.data.opened = true;
            $(this).find('div').html('&raquo;');
        }else{
            $('#article').removeClass('span12').addClass('span9');
            $('#topic').insertBefore($('#article')).show();
            e.data.opened = false;
            $(this).find('div').html('&laquo;');
        }
    });

    var headers = $('#index, #markdown-content').find('h1,h2,h3,h4,h5,h6');
     
    headers.hover(function(e){
        $(this).find('a.anchor').css('color', '#c60f0f');
    }, function(e){
        $(this).find('a.anchor').css('color', 'white');
    });

    //initialize popup
    $('.icon.help').popup();    
    
    //goto top
    $('#markdown-content').UItoTop({scrollSpeed: 500, text:'<i class="up icon"></i>' });
    
});
