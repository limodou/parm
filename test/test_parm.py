from __future__ import print_function
from __future__ import unicode_literals
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
    >>> print (parseHtml(text, '%(body)s', block_callback=blocks))
    <BLANKLINE>
    <pre class="linenums"><code class="language-python">$(function(){
        $('.div').on('click', function(e){
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
    >>> print (parseHtml(text, '%(body)s', block_callback=blocks))
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
    >>> print (parseHtml(text, '%(body)s', block_callback=blocks))
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
    });</code></pre>
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
    >>> print (parseHtml(text, '%(body)s', block_callback=blocks))
    <BLANKLINE>
    <pre><code>$(function(){
        $('.div').on('click', function(e){
            e.preventDefault();
    ...</code></pre>
    <BLANKLINE>
    """

def test_include_5():
    """
    >>> text = '''
    ... {% include file=test.js, lines=5-6%}
    ... ...e\.preventDefault
    ... {% endinclude %}
    ... '''
    >>> blocks = {'include':include}
    >>> print (parseHtml(text, '%(body)s', block_callback=blocks))
    <BLANKLINE>
    <pre><code>$(function(){
        $('.div').on('click', function(e){
            e.preventDefault();
    ...
                url:'/test',
                dataType:'json',
    ...</code></pre>
    <BLANKLINE>
    """

def test_include_6():
    """
    >>> text = '''
    ... {% include file=test.js %}
    ... \$\('\.div'\)...\$\.ajax
    ... {% endinclude %}
    ... '''
    >>> blocks = {'include':include}
    >>> print (parseHtml(text, '%(body)s', block_callback=blocks))
    <BLANKLINE>
    <pre><code>    $('.div').on('click', function(e){
            e.preventDefault();
            $.ajax({
    ...</code></pre>
    <BLANKLINE>
    """

def test_include_7():
    """
    >>> text = '''
    ... {% include file=test.js %}
    ... \$\('\.div'\)!...\$\.ajax!
    ... {% endinclude %}
    ... '''
    >>> blocks = {'include':include}
    >>> print (parseHtml(text, '%(body)s', block_callback=blocks))
    <BLANKLINE>
    <pre><code>...
            e.preventDefault();
    ...</code></pre>
    <BLANKLINE>
    """

def test_include_8():
    """
    >>> text = '''
    ... {% include file=test1.js %}
    ... <script>...</script>
    ... {% endinclude %}
    ... '''
    >>> blocks = {'include':include}
    >>> print (parseHtml(text, '%(body)s', block_callback=blocks))
    <BLANKLINE>
    <pre><code>...
    &lt;script&gt;
    avalon.define("blog", function(vm){
        vm.name = 'hello';
    });
    &lt;/script&gt;
    ...</code></pre>
    <BLANKLINE>
    """

