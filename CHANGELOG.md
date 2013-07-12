Parm Change Log
=====================

0.4 Version
-----------------

* upgrade with par 0.7, fix css and toc generation

0.3 Version
-----------------

* Add toc multiple column css support, you can pass class=multiple to toc, for example:

    ```
    {% toc max_depth=1,class="multiple3" %}
    file1.md
    file2.md
    file3.md
    {% endtoc %}
    ```

* Add cusome_css support, so you can pass your custom css in conf.py.

0.2 Version
-----------------

* Fix setup.py adding data files
* Fix heading 1 not found 
* Add source file view support
* Add rst2md sub command, it can convert rst to markdown

0.1 Version
-----------------
First version