parm
====

Convert par favorit markdown syntax to html document, also supports 
twitter bootstrap. 

How to Use
--------------

First install par and parm to your box.

```
pip install par
pip install parm
```

Then writing your markdown documents. For example write it in:

```
/project/docs
```

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

Next, you can start to convert the docs. Because parm support topic content, so
you can write your topic content in `index.md` file. The content just like:

```
Document Subject
==================

{% toc max_depth=2 %}
file1.md
file2.md
...
{% endtoc %}
```

You should put all files which you can to be listed in `toc` tag. And you can 
also set `max_depth` argumant, and it means the heading level of each markdown
file, such as `h1`, `h2`, .etc. You can also skip `max_depth` the default will 
be `1`.

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

Just try it, hope you enjoy it.
