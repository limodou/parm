from utils import log
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
    from uliweb import json_dumps
    
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
        if len(x['kwargs']) == 1 and x['kwargs'].keys()[0] != 'target':
            key = x['kwargs'].keys()[0]
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
    from uliweb import json_dumps
    
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
        if len(block['kwargs']) == 1 and block['kwargs'].keys()[0] != 'target':
            key = block['kwargs'].keys()[0]
        else:
            key = block['kwargs'].get('target', '')
        if key in data:
            data[key] = data[key].update(d)
        else:
            data[key] = d
        txt.append(json_dumps(data))
        txt.append('</script>')
        return '\n'.join(txt)
    else:
        return code_comment(visitor, block)

def toc(visitor, block, headers=None, relations=None):
    """
    Format:
        
        {% toc max_depth=2,class=multiple %}
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
            if x['id']:
                _id = '#'+x['id']
            else:
                _id = ''
            return '<li><a href="%s%s">%s</a></li>' % (x['link'], _id, x['title'])
        
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