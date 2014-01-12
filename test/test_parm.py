import sys
sys.path.insert(0, '..')
from par.md import parseHtml
from parm.md_ext import include

def test_include_1():
    """
    >>> text = '''
    ... {% include file=test.js, lines=1-2 5 10-, language=python, class=linenums  %}
    ... {% endinclude %}
    ... '''
    >>> blocks = {'include':include}
    >>> print parseHtml(text, '%(body)s', block_callback=blocks)
    <BLANKLINE>
    <pre class="linenums"><code class="language-python">$(function(){
    ...
                url:'/test',
    ...
            });
        });
    });</code></pre>
    <BLANKLINE>
    """

def test_include_2():
    """
    >>> text = '''
    ... {% include file=test.js %}
    ... {% endinclude %}
    ... '''
    >>> blocks = {'include':include}
    >>> print parseHtml(text, '%(body)s', block_callback=blocks)
    <BLANKLINE>
    <pre><code>$(function(){
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
    });</code></pre>
    <BLANKLINE>
    """

def test_include_3():
    """
    >>> text = '''
    ... {% include file=test.js%}
    ... \$\('\.div'\)...^\}\);
    ... {% endinclude %}
    ... '''
    >>> blocks = {'include':include}
    >>> print parseHtml(text, '%(body)s', block_callback=blocks)
    <BLANKLINE>
    <pre><code>    $('.div').on('click', function(e){
            e.preventDefault();
            $.ajax({
                url:'/test',
                dataType:'json',
                success:function(result){
                    show_message(result);
                }
            });
        });
    ...</code></pre>
    <BLANKLINE>
    """
    
def test_include_4():
    """
    >>> text = '''
    ... {% include file=test.js%}
    ... ...e\.preventDefault
    ... {% endinclude %}
    ... '''
    >>> blocks = {'include':include}
    >>> print parseHtml(text, '%(body)s', block_callback=blocks)
    <BLANKLINE>
    <pre><code>$(function(){
        $('.div').on('click', function(e){
    ...</code></pre>
    <BLANKLINE>
    """

def test_include_4():
    """
    >>> text = '''
    ... {% include file=test.js, lines=5-%}
    ... ...e\.preventDefault
    ... {% endinclude %}
    ... '''
    >>> blocks = {'include':include}
    >>> print parseHtml(text, '%(body)s', block_callback=blocks)
    <BLANKLINE>
    <pre><code>$(function(){
        $('.div').on('click', function(e){
    ...
                url:'/test',
                dataType:'json',
                success:function(result){
                    show_message(result);
                }
            });
        });
    });</code></pre>
    <BLANKLINE>
    """