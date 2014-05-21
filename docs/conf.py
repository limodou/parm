#coding=utf8
from __future__ import unicode_literals

"""
This config will be used for parm project settings.
You can change them to fit your needs.
"""

#available plugins
plugins = []

# The suffix of source filenames.
source_suffix = ['.md', '.markdown']

#template setttings
template_dirs = "templates"
templates = {'index':'index.html', '*':'default.html'}

tag_class = {
    
'table':'ui collapsing celled table segment',
'pre':'+prettyprint',

}

# pre code theme css only : sons-of-obsidian, sunburst
# can be found in static/asset directory
pre_css = 'sons-of-obsidian'

# The short X.Y version.
version = '1.4'

# General information about the project.
project = u'Parm'
project_url = './index.html'
copyright = u'2014, Limodou'
introduction = u'''
<h1 class="ui header">%s
<a class="ui black label">%s</a>
</h1>
<h2 class="ui header">Your project shows description here.</h2>
''' % (project, version)

# You can add custom css files, just like
# custom_css = ['/static/custom.css']
custom_css = []

# config menus
# format: ('name', 'caption', 'link')
menus = [
    ('home', 'Home', 'index.html'),
]

#page footer
footer = """
<p>Designed by Limodou, Copyright %s</p>
<p>CSS framework <a href="https://github.com/twitter/bootstrap">Bootstrap</a>, Markdown parser lib <a href="https://github.com/limodou/par">Par</a> and this page is created by <a href="https://github.com/limodou/parm">Parm</a> tool.</p>
""" % copyright

# The master toctree document.
master_doc = 'index'

#download source display
download_source = 'View Source'

#theme
#default will use semantic
#there are also bootstrap, semantic support
theme = 'semantic'

disqus = ''

#disqus support
#this use uliwebdoc, so you should replace it with your account name
disqus_text = '''<div id="disqus_thread" style="margin:20px;"></div>
 <script type="text/javascript">
     /* * * CONFIGURATION VARIABLES: EDIT BEFORE PASTING INTO YOUR WEBPAGE * * */
     var disqus_shortname = '%s'; // required: replace example with your forum shortname

     /* * * DON'T EDIT BELOW THIS LINE * * */
     (function() {
         var dsq = document.createElement('script'); dsq.type = 'text/javascript'; dsq.async = true;
         dsq.src = 'http://' + disqus_shortname + '.disqus.com/embed.js';
         (document.getElementsByTagName('head')[0] || document.getElementsByTagName('body')[0]).appendChild(dsq);
     })();
 </script>
 <noscript>Please enable JavaScript to view the <a href="http://disqus.com/?ref_noscript">comments powered by Disqus.</a></noscript>
 <a href="http://disqus.com" class="dsq-brlink">comments powered by <span class="logo-disqus">Disqus</span></a>
''' % disqus

#this use uliwebdoc, so you should replace it with your account name
disqus_js = '''<script type="text/javascript">
   /* * * CONFIGURATION VARIABLES: EDIT BEFORE PASTING INTO YOUR WEBPAGE * * */
   var disqus_shortname = '%s'; // required: replace example with your forum shortname

   /* * * DON'T EDIT BELOW THIS LINE * * */
   (function () {
       var s = document.createElement('script'); s.async = true;
       s.type = 'text/javascript';
       s.src = 'http://' + disqus_shortname + '.disqus.com/count.js';
       (document.getElementsByTagName('HEAD')[0] || document.getElementsByTagName('BODY')[0]).appendChild(s);
   }());
   </script>
''' % disqus

search = True
domain = 'limodou.github.io/parm'
search_html = """
<div class="item">
  <div class="ui icon input">
    <form id="searchform">
    <input name="q" type="text" placeholder="Search...">
    </form>
  </div>
</div>
"""

search_js = """
<script type="text/javascript">
$(function(){
    var form = $('#searchform');
    form.submit(function(e){
        e.preventDefault();
        var wq=$('input[name="q"]').val();
        var link="http://www.google.com/search?q=site:%s "+wq;
        window.open(link);

    });
});
</script>
""" % domain
