/* =========================================================
 * bootstrap-codecomment.js v1.0
 * =========================================================
 * Creating command point to code line or some keywords, and this will work with
 * google prettify javascript lib. It'll can be used in bootstrap environment.
 *
 * license BSD
 *   
 * author: limodou@gmail.com
 *   
 * requirement:
 *     jquery
 *     bootstrap
 *     prettify
 *     JSON2
 *       
 * comment data should be defined as
 *
 * <script id='id' type='texh/code-comment'>
 *  {"code id":
 *      {
 *          "1": "description",
 *          "key": "description"
 *      }
 *  }
 * </script>
 * ========================================================= */

!
function($) {

  "use strict"

  /* MODAL CLASS DEFINITION
   * ====================== */
  var comments = {};

  var CodeComment = function(content, options) {

      var that = this;
      this.options = options;
      this.$element = $(content);
      this.show();
    }

  CodeComment.prototype = {

    constructor: CodeComment
    , show: function(){
      var id = this.$element.attr('id') || '', that=this;
      var t = comments[id];
      if (t && this.$element[0].tagName != 'PRE'){
        var id = that.$element.data('rel');
        if (!t[id]) return;
        var content = t[id].content;
        if (content){
            this.$element.popup({content:content});
        }
      }
      else if (t){
        $.each(t, function(x, y){
            if (/\d+/.test(x)){
                var el = $('.linenums li:eq('+(parseInt(x)-1)+')', that.$element);
                if (el.size()>0){
                    el.css({position:'relative'});
                    var offset = el.offset()
                    var t;
                    if (parseInt(x)<10){
                        t = ' '+x;
                    }else{
                        t = x;
                    }
                    var item = $('<a href="#" class="para-comments-count">'+t+'.</a>')
                    .css({position:'absolute', left:-40}).click(function(e){e.preventDefault();});
                    item.popup({content:y.content||y});
                    $(el).prepend(item);
                }
            }else{
                $('.linenums span', that.$element).each(function(){
                    var t = $(this);
                    var r = new RegExp('\\b'+x+'\\b');
                    if (r.test(t.text())){
                        var item = ('<code class="nocode" style="background-color:blue;color:#fff;cursor:pointer;">'+x+'</code>');
                        t.html(t.text().replace(r, item));
                        $('code', t).popup({content:y.content||y});
                    }
                });
                
            }
        });
      }
    }
  }

  /* MODAL PRIVATE METHODS
   * ===================== */

  function init(){
    if ($.isEmptyObject(comments)){
      //calculate the comment points
      $('script[type="text/code-comment"]').each(function(i, v){
        var x = JSON.parse($(this).html());
        comments = $.extend(true, comments, x);
      });
    }
  }
  
  /* MODAL PLUGIN DEFINITION
   * ======================= */

  $.fn.code_comment = function(option) {
    var args = Array.prototype.slice.call(arguments);
    args.shift();
    init();
    /*
      return this.each(function() {
      var $this = $(this),
        data = $this.data('code_comment'),
        options = $.extend({}, $.fn.code_comment.defaults, typeof option == 'object' && option);
      if (!data) $this.data('code_comment', (data = new CodeComment(this, options)));
      if (typeof option == 'string') data[option].apply(data, args);
    })
    */
    var elements = this;
    var k = 0;
    var clock = Date;
    if (!clock['now']) {
      clock = { 'now': function () { return +(new Date); } };
    }
    
    function do_work(){
        var endTime = clock['now']() + 250; /* ms */
        
        for(; k<elements.length && clock['now']()<endTime; k++){
            var $this = $(elements[k]);
            var data = $this.data('code_comment');
            var options = $.extend({}, $.fn.code_comment.defaults, typeof option == 'object' && option);
            if (!data) $this.data('code_comment', (data = new CodeComment($this, options)));
//            if (typeof option == 'string') data[option].apply(data, args);
            
        }
        if (k<elements.length){
            setTimeout(do_work, 250);
        }
    }
    do_work();
  }

  $.fn.code_comment.defaults = {
  }

  $.fn.code_comment.Constructor = CodeComment;

}(window.jQuery);
