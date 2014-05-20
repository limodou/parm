# -*- coding: utf-8 -*-
from __future__ import unicode_literals

"""Simple Markdown writer for reStructuredText."""

__docformat__ = 'reStructuredText'

from docutils import frontend, nodes, writers, languages
from docutils.parsers.rst import Directive, directives

class Writer(writers.Writer):

    supported = ('markdown',)
    """Formats this writer supports."""

    output = None
    """Final translated form of `document`."""

    # Add configuration settings for additional Markdown flavours here.
    settings_spec = (
        'Markdown-Specific Options',
        None,
        (('Extended Markdown syntax.',
          ['--extended-markdown'],
          {'default': 0, 'action': 'store_true',
           'validator': frontend.validate_boolean}),
         ('Strict Markdown syntax. Default: true',
          ['--strict-markdown'],
          {'default': 1, 'action': 'store_true',
           'validator': frontend.validate_boolean}),))

    def __init__(self):
        writers.Writer.__init__(self)
        self.translator_class = Translator

    def translate(self):
        visitor = self.translator_class(self.document)
        self.document.walkabout(visitor)
        self.output = visitor.astext()

#register toctree, in order to process sphinx

class toctree(nodes.General, nodes.Text):pass

class Toctree(Directive):
    has_content = True
    required_arguments = 0
    optional_arguments = 0
    final_argument_whitespace = False
    option_spec = {
        'maxdepth': int,
    }
    def run(self):
        max_depth = self.options.get('maxdepth', 1)
        text = ['{%% toc max_depth=%d %%}' % max_depth]+[x for x in self.content]+['{% endtoc %}']
        node = toctree('\n'.join(text))
        return [node]

directives.register_directive('toctree', Toctree)

class Translator(nodes.NodeVisitor):

    def __init__(self, document):
        nodes.NodeVisitor.__init__(self, document)
        self.settings = settings = document.settings
        lcode = settings.language_code
        self.language = languages.get_language(lcode, document.reporter)

        self.head = []
        self.body = []
        self.foot = []
        self.list_type = []
        self.indent = 0
        self.first_indent = True

        self.section_level = 0

        ##TODO docinfo items can go in a footer HTML element (store in self.foot).
        self._docinfo = {
            'title' : '',
            'subtitle' : '',
            'author' : [],
            'date' : '',
            'copyright' : '',
            'version' : '',
            }

        # Customise Markdown syntax here. Still need to add literal, term,
        # indent, problematic etc...
        self.defs = {
            'emphasis': ('*', '*'),   # Could also use ('_', '_')
            'problematic' : ('\n\n', '\n\n'),
            'strong' : ('**', '**'),  # Could also use ('__', '__')
            'subscript' : ('<sub>', '</sub>'),
            'superscript' : ('<sup>', '</sup>'),
            }

    # Utility methods

    def astext(self):
        """Return the final formatted document as a string."""
        return ''.join(self.head + self.body + self.foot)

    def deunicode(self, text):
        text = text.replace(u'\xa0', ' ')
        text = text.replace(u'\u2020', '\\(dg')
        return text

    def ensure_eol(self):
        """Ensure the last line in body is terminated by new line."""
        if self.body and self.body[-1][-1] != '\n':
            self.body.append('\n')

    def indent_text(self, text, indent=0, prefix='', first=True):
        """
        Splite text into lines, and indent them with prefix string
        """
        lines = text.splitlines()
        if first:
            return '\n'.join([' '*indent*4+prefix+x for x in lines])
        else:
            return '\n'.join([lines[0]] + [' '*indent*4+prefix+x for x in lines[1:]])
        
    def set_class_on_child(self, node, class_, index=0):
        """
        Set class `class_` on the visible child no. index of `node`.
        Do nothing if node has fewer children than `index`.
        """
        children = [n for n in node if not isinstance(n, nodes.Invisible)]
        try:
            child = children[index]
        except IndexError:
            return
        child['classes'].append(class_)

    def set_first_last(self, node):
        self.set_class_on_child(node, 'first', 0)
        self.set_class_on_child(node, 'last', -1)

    # Node visitor methods

    def visit_Text(self, node):
        text = node.astext()
        self.body.append(text)

    def depart_Text(self, node):
        pass

    def visit_comment(self, node):
        self.body.append('<!-- ' + node.astext() + ' -->\n')
        raise nodes.SkipNode

    def visit_docinfo_item(self, node, name):
        if name == 'author':
            self._docinfo[name].append(node.astext())
        else:
            self._docinfo[name] = node.astext()
        raise nodes.SkipNode

    def visit_document(self, node):
        pass

    def depart_document(self, node):
        pass

    def visit_emphasis(self, node):
        self.body.append(self.defs['emphasis'][0])

    def depart_emphasis(self, node):
        self.body.append(self.defs['emphasis'][1])

    def walk_text(self, node):
        backup = self.body
        self.body = []
        for c in node.children:
            c.walkabout(self)
        text = ''.join(self.body)
        self.body = backup
        return text
    
    def visit_paragraph(self, node):
        text = self.walk_text(node)
            
        #self.ensure_eol()
        if self.indent:
            self.body.append(self.indent_text(text, self.indent, first=self.first_indent))
            self.body.append('\n')
            self.first_indent = True
            raise nodes.SkipNode

    def depart_paragraph(self, node):
        self.body.append('\n\n')

    def visit_problematic(self, node):
        self.body.append(self.defs['problematic'][0])

    def depart_problematic(self, node):
        self.body.append(self.defs['problematic'][1])

    def visit_section(self, node):
        self.section_level += 1

    def depart_section(self, node):
        self.section_level -= 1

    def visit_strong(self, node):
        self.body.append(self.defs['strong'][0])

    def depart_strong(self, node):
        self.body.append(self.defs['strong'][1])

    def visit_subscript(self, node):
        self.body.append(self.defs['subscript'][0])

    def depart_subscript(self, node):
        self.body.append(self.defs['subscript'][1])

    def visit_subtitle(self, node):
        if isinstance(node.parent, nodes.document):
            self.visit_docinfo_item(node, 'subtitle')
            raise nodes.SkipNode

    def visit_superscript(self, node):
        self.body.append(self.defs['superscript'][0])

    def depart_superscript(self, node):
        self.body.append(self.defs['superscript'][1])

    def visit_system_message(self, node):
        # TODO add report_level
        #if node['level'] < self.document.reporter['writer'].report_level:
        #    Level is too low to display:
        #    raise nodes.SkipNode
        attr = {}
        backref_text = ''
        if node.hasattr('id'):
            attr['name'] = node['id']
        if node.hasattr('line'):
            line = ', line %s' % node['line']
        else:
            line = ''
        self.body.append('"System Message: %s/%s (%s:%s)"\n'
            % (node['type'], node['level'], node['source'], line))

    def depart_system_message(self, node):
        pass

    def visit_title(self, node):
        if self.section_level == 0:
            self.head.append(u'# {0}\n'.format(node.astext()))
            self._docinfo['title'] = node.astext()
            self.body.append('\n')
            raise nodes.SkipNode
        else:
            self.body.append(u'\n{0} {1}\n'.format((self.section_level+1)*'#',
                self.deunicode(node.astext()).split(' ', 1)[-1].strip()))
            self.body.append('\n')
            raise nodes.SkipNode

    def depart_title(self, node):
        self.body.append('\n')

    def visit_transition(self, node):
        # Simply replace a transition by a horizontal rule.
        # Could use three or more '*', '_' or '-'.
        self.body.append('\n---\n\n')
        raise nodes.SkipNode

    #parm support
    def visit_definition(self, node):
        self.body.append(self.indent*4*' ')
        self.indent += 1

    def depart_definition(self, node):
        self.body.append('\n')
        self.indent -= 1

    def visit_definition_list(self, node):
        self.body.append('\n')

    def depart_definition_list(self, node):
        self.body.append('\n')

    def visit_definition_list_item(self, node):
        pass

    def depart_definition_list_item(self, node):
        pass

    def visit_term(self, node):
        self.body.append(self.indent*4*' ')

    def depart_term(self, node):
        self.body.append(' --\n')

    def visit_enumerated_list(self, node):
        self.list_type.append('number')
        self.body.append('\n')
        self.indent += 1

    def depart_enumerated_list(self, node):
        self.list_type.pop()
        self.body.append('\n')
        self.indent -= 1

    def visit_bullet_list(self, node):
        self.list_type.append('bullet')
        self.body.append('\n')
        self.indent += 1
        
    def depart_bullet_list(self, node):
        self.list_type.pop()
        self.body.append('\n')
        self.indent -= 1

    def visit_list_item(self, node):
        if self.list_type[-1] == 'number':
            self.body.append((self.indent-1)*4*' '+'1. ')
        else:
            self.body.append((self.indent-1)*4*' '+'* ')
        self.first_indent = False

    def depart_list_item(self, node):
        self.first_indent = True

    def visit_literal_block(self, node):
        self.body.append('\n')
        self.body.append(self.indent_text('```\n'+node.astext()+'\n```', self.indent))
        self.body.append('\n\n')
        raise nodes.SkipNode

    def visit_literal(self, node):
        self.body.append('`')

    def depart_literal(self, node):
        self.body.append('`')
        
    def visit_block_quote(self, node):
        children = [n for n in node if not isinstance(n, nodes.Invisible)]
        if children[0].tagname not in ('bullet_list', 'enumerated_list', 'definition_list'):
            self.body.append('\n')
            self.body.append(self.indent_text(node.astext(), self.indent, '> '))
            self.body.append('\n')
            raise nodes.SkipNode
        
    def depart_block_quote(self, node):
        pass
    
    def visit_toctree(self, node):
        self.body.append('\n')
        self.body.append(node.astext().replace('.rst', '.md'))
        self.body.append('\n\n')
        raise nodes.SkipNode
        
    def depart_toctree(self, node):
        pass
    
    def visit_reference(self, node):
        url = node['refuri']
        if url.startswith('mailto:'):
            self.body.append('%s' % url)
        else:
            self.body.append('[%s](%s)' % (node.astext(), url))
        raise nodes.SkipNode
    
    def visit_note(self, node):
        self.body.append('\n')
        self.body.append(self.indent*4*' ')
        self.body.append('{% alert class=info %}\n')
        
    def depart_note(self, node):
        self.body.append(self.indent*4*' ')
        self.body.append('{% endalert %}\n\n')

    def visit_attention(self, node):
        self.body.append('\n')
        self.body.append(self.indent*4*' ')
        self.body.append('{% alert class=warning %}\n')
        
    def depart_attention(self, node):
        self.body.append(self.indent*4*' ')
        self.body.append('{% endalert %}\n\n')

    def visit_image(self, node):
        url = node['uri']
        self.body.append('\n![image](%s)\n\n' % url)
        raise nodes.SkipNode
        
    def depart_image(self, node):
        pass
    
    def visit_table(self, node):
        self.ensure_eol()
        self.body.append('\n')
    
    def depart_table(self, node):
        self.body.append('\n')
    
    def visit_row(self, node):
        self.body.append(self.indent*4*' ')
        self.body.append('||')
    
    def depart_row(self, node):
        self.body.append('\n')
        
    def visit_entry(self, node):
        self.body.append(' ')
        self.body.append(self.walk_text(node).strip())
        self.body.append(' ||')
        raise nodes.SkipNode
    
    def depart_entry(self, node):
        pass
        
    def visit_tgroup(self, node):
        pass
    
    def depart_tgroup(self, node):
        pass
    
    def visit_tbody(self, node):
        pass
    
    def depart_tbody(self, node):
        pass

    def visit_thead(self, node):
        pass
    
    def depart_thead(self, node):
        pass
    
    def visit_colspec(self, node):
        pass
    
    def depart_colspec(self, node):
        pass
    
# The following code adds visit/depart methods for any reSturcturedText element
# which we have not explicitly implemented above.

# All reStructuredText elements:
rst_elements = ('abbreviation', 'acronym', 'address', 'admonition',
    'attention', 'attribution', 'author', 'authors', 'block_quote', 
    'bullet_list', 'caption', 'caution', 'citation', 'citation_reference', 
    'classifier', 'colspec', 'comment', 'compound', 'contact', 'container', 
    'copyright', 'danger', 'date', 'decoration', 'definition',
    'definition_list', 'definition_list_item', 'description', 'docinfo', 
    'doctest_block', 'document', 'emphasis', 'entry', 'enumerated_list', 
    'error', 'field', 'field_body', 'field_list', 'field_name', 'figure', 
    'footer', 'footnote', 'footnote_reference', 'generated', 'header', 
    'hint', 'image', 'important', 'inline', 'label', 'legend', 'line', 
    'line_block', 'list_item', 'literal', 'literal_block', 'math', 
    'math_block', 'note', 'option' ,'option_argument', 'option_group', 
    'option_list', 'option_list_item', 'option_string', 'organization', 
    'paragraph', 'pending', 'problematic', 'raw', 'reference', 'revision', 
    'row', 'rubric', 'section', 'sidebar', 'status', 'strong', 'subscript', 
    'substitution_definition', 'substitution_reference', 'subtitle', 
    'superscript', 'system_message', 'table', 'target', 'tbody,' 'term', 
    'tgroup', 'thead', 'tip', 'title', 'title_reference', 'topic', 
    'transition','version','warning',)

##TODO Eventually we should silently ignore unsupported reStructuredText 
##     constructs and document somewhere that they are not supported.
##     In the meantime raise a warning *once* for each unsupported element.
_warned = set()

def visit_unsupported(self, node):
    node_type = node.__class__.__name__
    if node_type not in _warned:
        self.document.reporter.warning('\nThe ' + node_type + \
            ' element is not supported. \nText:\n%s\n---\n' % node.astext()[:70])
        _warned.add(node_type)
    raise nodes.SkipNode

for element in rst_elements:
    if not hasattr(Translator, 'visit_' + element):
        setattr(Translator, 'visit_' + element , visit_unsupported)

