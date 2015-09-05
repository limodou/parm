Change Log
=====================

1.7 Version
-----------------

* Add [mermaid](https://github.com/knsv/mermaid) support

For example:

```
{% mermaid %}
graph TD;
    A-->B;
    A-->C;
    B-->D;
    C-->D;
{% endmermaid %}
```

will render to:

{% mermaid %}
graph TD;
    A-->B;
    A-->C;
    B-->D;
    C-->D;
{% endmermaid %}

```
{% mermaid %}
sequenceDiagram
    participant Alice
    participant Bob
    Alice->John: Hello John, how are you?
    loop Healthcheck
        John->John: Fight against hypochondria
    end
    Note right of John: Rational thoughts <br/>prevail...
    John-->Alice: Great!
    John->Bob: How about you?
    Bob-->John: Jolly good!
{% endmermaid %}
```

will render to:

{% mermaid %}
sequenceDiagram
    participant Alice
    participant Bob
    Alice->John: Hello John, how are you?
    loop Healthcheck
        John->John: Fight against hypochondria
    end
    Note right of John: Rational thoughts <br/>prevail...
    John-->Alice: Great!
    John->Bob: How about you?
    Bob-->John: Jolly good!
{% endmermaid %}


```
{% mermaid %}
        gantt
        dateFormat  YYYY-MM-DD
        title Adding GANTT diagram functionality to mermaid
        section A section
        Completed task            :done,    des1, 2014-01-06,2014-01-08
        Active task               :active,  des2, 2014-01-09, 3d
        Future task               :         des3, after des2, 5d
        Future task2               :         des4, after des3, 5d
        section Critical tasks
        Completed task in the critical line :crit, done, 2014-01-06,24h
        Implement parser and jison          :crit, done, after des1, 2d
        Create tests for parser             :crit, active, 3d
        Future task in critical line        :crit, 5d
        Create tests for renderer           :2d
        Add to mermaid                      :1d
{% endmermaid %}
```

will render to:

{% mermaid %}
        gantt
        dateFormat  YYYY-MM-DD
        title Adding GANTT diagram functionality to mermaid
        section A section
        Completed task            :done,    des1, 2014-01-06,2014-01-08
        Active task               :active,  des2, 2014-01-09, 3d
        Future task               :         des3, after des2, 5d
        Future task2               :         des4, after des3, 5d
        section Critical tasks
        Completed task in the critical line :crit, done, 2014-01-06,24h
        Implement parser and jison          :crit, done, after des1, 2d
        Create tests for parser             :crit, active, 3d
        Future task in critical line        :crit, 5d
        Create tests for renderer           :2d
        Add to mermaid                      :1d
{% endmermaid %}

1.6 Version
-----------------

* Remove bootstrap theme
* Add check and radio icon in list. you can define them like

    ```
    * [*] checkbox with checked
      * <*> radio with checked
    * [ ] checkbox without checked
    * [] checkbox without checked
    * < > radio without checked
    * <> radio without checked
    ```

1.5.1 Version
-----------------

* Fix `open()` bug in windows platform, missing encoding parameter, default will by 'utf8'
  and you can change it in `conf.py` for `encoding` variable.

1.5 Version
-----------------

* Refactor with _compat.py

1.4 Version
-----------------

* Support py2&3

1.3 Version
-----------------

* Fix disqus not defined when init bug. You can just change it in conf.py later.
* Upgrade semantic-ui to 0.15.1
* Fix `include` rule
* Fix comment.js bug in sementic-ui theme.
* Add press `h` to goto index.html support.
* Add goto top support.

1.2 Version
-----------------

* Fix `include` bug
* Fix `class=linenums` bug

1.1 Version
-----------------

* Add `include` syntax, so that you can include source code to markdown file, 
  for example:

    ```
    {% include file=test.js, lines=1-2 10-, language=python, class=linenums  %}
    {% endinclude %}
    ```
    
    `class=linenums` is used to display line number. 
    
    The simplest format is:
    
    ```
    {% include file=test.js %}
    {% endinclude %}
    ```
    
    Also support regular expression, for example:
    
    ```
    {% include file=test.js%}re.
    \$\('\.div'\)...^\}\);
    {% endinclude %}
    ```
    
    parm will not automatically escape special characters such as `{()}` etc.
    And you should separate begin pattern and end pattern with `...`. Extra blank
    before the pattern will not skipped, but ending blank will be trimmed.
    
* Add `test_parm.py` file to test `include` syntax.
* Fix customized `prettify.css` bug in semantic theme

1.0 Version
-----------------

* Change `setup.py`, add `par` package requirement.
* Add google search support, you can config it via init command by default.
* Fix `rst2md` parsing `.. contents::` bug.
* Change `rst2md` and `make` command parameter.

0.9.1 Version
-----------------

* Bug fix

0.9 Version
-----------------

* Add exclude support
* Fix readme
* Add disqus config support

0.8 Version
-----------------

* Add semantic theme

0.7 Version
-----------------

* Fix sub directory link bug
* Remove anchor in title of index.html
* Fix source file copy bug
* Fix scroll offset bug

0.6 Version
-----------------

* Fix make command, copy all directories to output directory excep for template_dir

0.5 Version
-----------------

* upgrade css to suit with responsable
* add files parameters to make command

0.4 Version
-----------------

* upgrade with par 0.7, fix css and toc generation
* add sub directories support for source

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