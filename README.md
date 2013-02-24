parm
====

Convert par favorit markdown syntax to html document, also supports 
twitter bootstrap. 

## Installation

First install par and parm to your box.

```
pip install par
pip install parm
```

Then writing your markdown documents. For example write it in:

```
/project/docs
```

## Initialize Environment

Next, change to docs folder. If you are run the first time, you should initialize
parm project environment, just like:

```
parm init
```

When running this command, it'll may ask if you want to initialize the config 
information, if you choice `Y`, then you will enter interactive command line, 
then just input some infos, and you can change them later in `conf.py` file.
And parm will use it to convert the markdown documents.

This command will copy some static files and templates from parm module. But
you don't need to care about them now.

## Writing TOC

Next, you can start to convert the docs. Because parm support table of content(TOC), so
you can write your topic content in `index.md` file. The content just like:

```
Document Subject
==================

{% toc max_depth=2[,class=multiple] %}
file1.md
file2.md
...
{% endtoc %}
```

You should put all files which you can to be listed in `toc` tag. And you can 
also set `max_depth` argumant, and it means the heading level of each markdown
file, such as `h1`, `h2`, .etc. You can also skip `max_depth` the default will 
be `1`.

`,class=multiple` is optional. By default, the toc indexes will be output one column.
If you want to display multiple columns, you can pass `,class=multiple` . There
are 3 parameters: `multiple`, `multiple2`, `multiple3`. `multiple` and `multiple2`
are the same, they'll output indexes for two columns. And `multiple3` for 3 columns.

## Build

And you can run:

```
parm make
```

to start converting.

And when the convert finished, the result will be output to `../html` default.
You can also change it with `-d` parameter, just like:

```
parm make -d output_directory
```

and the result will be outputed to  `output_directory`.

## Convert reStructuredText to Markdown

parm also supports convert reStructuredText format to Markdown format. Just
enter your doc directory, and execute below command:

```
parm rst2md <output_directory>
```

But you known, reStructuredText format is rich than markdown, so I expand some
new style for Markdown format in `par` project. But there are still some styles
unsupported by par, so you need to change them manually.

And if you want to convert reStructuredText to Markdown, you should install 
`docutils` first.

Just try it, hope you enjoy it.

## About rst2md writer

I found there is a project https://github.com/cgwrench/rst2md in github, and I
changed the code from it in order to suit the style format of `par`. But I found
rst2md seem not so matual enough.

## Demo site

Uliweb-doc is written by markdown, and using parm convert to html files. You can
see http://limodou.github.com/uliweb-doc, and the source code is in 
https://github.com/limodou/uliweb-doc.

## How to add disqus

When init the parm project, will include some templates and static files. You may
want to add disqus support to each page. So let's show you how to do that.

### Sign in Disqus and got embeded codes

And you'll get two paragraphs, one is html code, the other is js code. For example:

**html code**

```
<div id="disqus_thread" style="margin:20px;"></div>
 <script type="text/javascript">
     /* * * CONFIGURATION VARIABLES: EDIT BEFORE PASTING INTO YOUR WEBPAGE * * */
     var disqus_shortname = 'YOUR_SITE_SHORT_NAME'; // required: replace example with your forum shortname

     /* * * DON'T EDIT BELOW THIS LINE * * */
     (function() {
         var dsq = document.createElement('script'); dsq.type = 'text/javascript'; dsq.async = true;
         dsq.src = 'http://' + disqus_shortname + '.disqus.com/embed.js';
         (document.getElementsByTagName('head')[0] || document.getElementsByTagName('body')[0]).appendChild(dsq);
     })();
 </script>
 <noscript>Please enable JavaScript to view the <a href="http://disqus.com/?ref_noscript">comments powered by Disqus.</a></noscript>
 <a href="http://disqus.com" class="dsq-brlink">comments powered by <span class="logo-disqus">Disqus</span></a>
```

**js code**

```
<script type="text/javascript">
   /* * * CONFIGURATION VARIABLES: EDIT BEFORE PASTING INTO YOUR WEBPAGE * * */
   var disqus_shortname = 'YOUR_SITE_SHORT_NAME'; // required: replace example with your forum shortname

   /* * * DON'T EDIT BELOW THIS LINE * * */
   (function () {
       var s = document.createElement('script'); s.async = true;
       s.type = 'text/javascript';
       s.src = 'http://' + disqus_shortname + '.disqus.com/count.js';
       (document.getElementsByTagName('HEAD')[0] || document.getElementsByTagName('BODY')[0]).appendChild(s);
   }());
   </script>
```

And you should replace two `YOUR_SITE_SHORT_NAME` according your account of disqus.

### Change layout.html

Open the template file `your_parm_project/_build/layout.html` and change two 
places:

After

```
<div class="source">
    <i class="icon-download"></i>{{<< source}}
</div>
```

add:

```
<!-- disqus -->
{{<< conf.disqus_text}}
```

And before

```
</body>
```

add:

```
{{<< conf.disqus_js}}
```

When after above works, execute `parm make -d output_directory` again.
