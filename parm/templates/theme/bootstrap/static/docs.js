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

var sidemenu = function (element, level) {
    var el = $(element),
        buf = [],
        selector = level || 'h2,h3', stack = [],
        items,
        i, len, item
        name, last=''

    items = $(selector)
    buf.push('<nav class="bs-docs-sidebar hidden-print hidden-xs hidden-sm affix-top">')
    buf.push('<ul class="nav bs-docs-sidenav">')

    for(var i=0, len=items.length; i<len; i++) {
      item = items[i]
      name = item.tagName
      if (i == 0)
        stack.push(name)
      if (last && last<name) { //new
        buf.push('<ul class="nav">')
        stack.push(name)
      } else if (last && last > name) {
        buf.push('</ul>')
        stack.pop()
      } else if (last) {
        buf.push('</li>')
      }
      buf.push('<li><a href="#' + $(item).attr('id') + '">' + item.childNodes[0].textContent + '</a>')
      last = name
    }
    for(var i=stack.length-1; i>0; i--) {
      buf.push('</ul></li>')
      stack.pop()
    }
    if (stack.length == 1)
      buf.push('</li>')

    el.html(buf.join('\n'))
}

$(function(){

    // make code pretty
    window.prettyPrint && prettyPrint()

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


    //header process
    sidemenu('#toc', 'h2,h3')

    var $window = $(window)
    var $body   = $(document.body)

    $body.scrollspy({
      target: '.bs-docs-sidebar'
    })
    $window.on('load', function () {
      $body.scrollspy('refresh')
    })

    // Sidenav affixing
    setTimeout(function () {
      var $sideBar = $('.bs-docs-sidebar')

      $sideBar.affix({
        offset: {
          top: function () {
            var offsetTop      = $sideBar.offset().top
            var sideBarMargin  = parseInt($sideBar.children(0).css('margin-top'), 10)
            var navOuterHeight = $('.bs-docs-nav').height()

            return (this.top = offsetTop - navOuterHeight - sideBarMargin)
          },
          bottom: function () {
            return (this.bottom = $('.bs-docs-footer').outerHeight(true))
          }
        }
      })
    }, 100)

    setTimeout(function () {
      $('.bs-top').affix()
    }, 100)


    //goto top
    $('#markdown-content').UItoTop({scrollSpeed: 500, text:'<i class="fa fa-arrow-up"></i>' });
    
});
