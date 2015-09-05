from __future__ import absolute_import, unicode_literals
from ._compat import range, open
from .utils import log
import re
import os

def mermaid(visitor, block):
    """
    Format:
        
        {% mermaid %}
        graph TD;
            A-->B;
            A-->C;
            B-->D;
            C-->D;
        {% endmermaid %}
        
    """
    from .utils import json_dumps
    
    txt = []
    txt.append('<div class="mermaid">')
    txt.append(block['body'])
    txt.append('</div>')
    return '\n'.join(txt)

