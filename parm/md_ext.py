from __future__ import absolute_import, unicode_literals
from ._compat import range, open, u
from .utils import log
import re
import os

def code_comment(visitor, items):
    """
    Format:
        
        [[code-comment(target=pre element id)]]:
            key : value
            key : value
            
        or:
            
        [[code-comment(pre element id)]]:
            key : value
            key : value
        
    """
    from .utils import json_dumps
    
    txt = []
    data = {}
    txt.append('<script type="text/code-comment">')
    for x in items:
        d = {}
        for line in x['body'].splitlines():
            if line.strip():
                k, v = line.split(':', 1)
                k = k.strip()
                if '=' in v:
                    title, v = v.split('=', 1)
                    title = title.strip()
                else:
                    title = k
                v = visitor.parse_text(v.strip(), 'article')
                d[k] = {'title':title, 'content':v}
        if len(x['kwargs']) == 1 and list(x['kwargs'].keys())[0] != 'target':
            key = list(x['kwargs'].keys())[0]
        else:
            key = x['kwargs'].get('target', '')
        if key in data:
            data[key] = data[key].update(d)
        else:
            data[key] = d
    txt.append(json_dumps(data))
    txt.append('</script>')
    return '\n'.join(txt)

def new_code_comment(visitor, block):
    """
    Format:
        
        {% code-comment target=pre element id %}
        key : value
        key : value
        {% endcode-comment %}    
        
    """
    from .utils import json_dumps
    
    if 'new' in block:
        
        txt = []
        data = {}
        txt.append('<script type="text/code-comment">')
        d = {}
        for line in block['body'].splitlines():
            if line.strip():
                k, v = line.split(':', 1)
                k = k.strip()
                if '=' in v:
                    title, v = v.split('=', 1)
                    title = title.strip()
                else:
                    title = k
                v = visitor.parse_text(v.strip(), 'article')
                d[k] = {'title':title, 'content':v}
        if len(block['kwargs']) == 1 and list(block['kwargs'].keys())[0] != 'target':
            key = list(block['kwargs'].keys())[0]
        else:
            key = block['kwargs'].get('target', '')
        if key in data:
            data[key] = data[key].update(d)
        else:
            data[key] = d
        txt.append(u(json_dumps(data)))
        txt.append('</script>')
        return '\n'.join(txt)
    else:
        return code_comment(visitor, block)

def code(visitor, block):
    """
    Format:

        {% code %}
        code
        {% endcode %}

    """
    from .utils import json_dumps

    return block['body']

def toc(visitor, block, headers=None, relations=None):
    """
    Format:
        
        {% toc max_depth=2 %}
        file1.md
        file2.md
        {% endtoc %}
    """
    s = []
    s.append('<div class="toc">\n')
    depth = int(block['kwargs'].get('max_depth', '1'))
    if 'class' in block['kwargs']:
        s.append('<ul class=%s>\n' % block['kwargs']['class'])
    else:
        s.append('<ul>\n')
    prev = {'prev':{}, 'next':{}, 'current':{}}
    
    for fname in block['body'].splitlines():
        hs = headers.get(fname, [])
        if not hs:
            log.error("File %s can't be found, will be skipped" % fname)
            continue
        
        def make_title(x):
            return '<li><a href="%s">%s</a></li>' % (x['link'], x['title'])
        
        _fname, _ext = os.path.splitext(fname)
        last = 1
        title = _fname
        for x in hs:
            level = x['level']
            
            #fetch title, so an article should be one h1 subject
            if level == 1:
                title = x['title']
                
            if level > depth:
                continue
            if level == last: #same
                s.append(make_title(x))
            elif level == last-1: #reindent
                s.append('</ul>\n')
                s.append(make_title(x))
                last -= 1
            elif level == last+1: #indent
                s.append('<ul>\n')
                s.append(make_title(x))
                last += 1
            else:
                pass
        for i in range(last, 1, -1):
            s.append('</ul>\n')
            
        #process prev and next
        c = {'link':_fname+'.html', 'title':title}
        current = relations[_fname] = {
            'prev':{}, 'next':{}, 
            'current':c,
        }
        p = prev['current']
        if p:
            current['prev'] = {'link':p['link'], 'title':p['title']}
        prev['next'] = c
        prev = current
    s.append('</ul>\n')
    s.append('</div>\n')
    return ''.join(s)

def include(visitor, block):
    """
    include source code from file, the format is:
        
        {% include file=test.js, lines=1-20 30-, language=python, class=linenums %}
        lines_content
        {% endinclude %}
        
        the line 1<= lineno <= 20 and 30 <= lineno will be included
        
        lines_content is line pattern used to match which lines should be included
        the format is:
            
            begin ... end
            
        if you don't want to included `begin` or `end` line, you can add `!` at the 
        end of `begin` or `end`
            
        begin and end are line pattern, and end will not be included
    """
    
    def get_lineno(lines):
        num = []
        for x in lines.split():
            if '-' in x:
                b, e = x.split('-')
                if b.strip():
                    b = int(b)
                else:
                    b = 1
                b = int(b)
                if e.strip():
                    e = int(e)
                else:
                    e = -1
                num.append((b, e))
            else:
                num.append((int(x), int(x)))
        return num
        
    def get_line_index(line, v, index, flag=''):
        """
        flag is 'begin' or 'end'
        """
        if isinstance(v, int):
            return v
        skip = False
        p = v
        if v.endswith('!'):
            skip = True
            p = v[:-1]
            
        if re.search(p, line):
            if skip:
                if flag == 'begin':
                    index = index + 1
                elif flag == 'end':
                    index = index - 1
            return index
        else:
            return v
        
    def test_lineno(n, lineno, index):
        """
        last status
        """
        if index != -1:
            b, e = lineno[index]
            if b<=n and ((e==-1) or n<=e):
                return True, index
        for i, v in enumerate(lineno):
            b, e = lineno[i]
            if b<=n and ((e==-1) or n<=e):
                return True, i
                
        return False, -1
        
    kw = block['kwargs']
    filename = kw.pop('file', '')
    if visitor.filename:
        _dir = os.path.dirname(visitor.filename)
        filename = os.path.join(_dir, filename)
    if not os.path.exists(filename):
        log.error("Can't find the file %s" % filename)
        return '<p class="error">Can\'t find the file %s</p>' % filename
    
    #Get line number array
    lines = kw.pop('lines', '')
    if lines:
        lineno = get_lineno(lines)
    else:
        lineno = []
    
    #process lines_content
    pattern = False
    for x in block['body'].splitlines():
        x = x.rstrip()
        if x:
            v = x.split('...')
            if len(v) == 1:
                b = x
                e = ''
            else:
                b, e = [y.rstrip() for y in v]
            if b.isdigit():
                b = int(b)
            else:
                pattern = True
            b = b or 1
            if e.isdigit():
                e = int(e)
            else:
                pattern = True
            e = e or -1
            if len(v) == 1:
                lineno.append(b)
            else:
                lineno.append((b, e))

    s = []
    first = '```'
    lang = kw.pop('language', '')
    if lang:
        first += lang+','
    x = []
    for k, v in kw.items():
        x.append('%s=%s' % (k, v))
    if x:
        first += ','.join(x)
    s.append(first)
    
    with open(filename, 'r') as f:
        buf = f.readlines()
    
    if lineno and pattern:
        #calculate patterns
        for i, line in enumerate(buf):
            for j, v in enumerate(lineno):
                if isinstance(v, tuple):
                    lineno[j] = (get_line_index(line, v[0], i+1, 'begin'), get_line_index(line, v[1], i+1, 'end'))
                else:
                    t = get_line_index(line, v, i+1)
                    lineno[j] = t, t
        
        for i in range(len(lineno)-1, -1, -1):
            v = lineno[i]
            if not isinstance(v, tuple):
                del lineno[i]
            else:
                if isinstance(v[0], str) or isinstance(v[1], str):
                    del lineno[i]
       
    last_index = -1
    for i, line in enumerate(buf):
        line = line.rstrip()
        if not lineno:
            s.append(line)
        else:
            flag, index = test_lineno(i+1, lineno, last_index)
            if flag:
                s.append(line)
                last_index = index
            else:
                if i-1>=0 and s[-1]!='...':
                    s.append('...')
                last_index = -1
    s.append('```')
    text = '\n'.join(s)
    return visitor.parse_text(text, 'article')
    
