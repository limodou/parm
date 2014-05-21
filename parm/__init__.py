#! /usr/bin/env python
#coding=utf-8
#
# Author: limodou@gmail.com
# This program is based on pyPEG
#
# license: BSD
#
from __future__ import print_function
from __future__ import absolute_import
from __future__ import unicode_literals
from future.builtins import str, open
import os, sys
import re
sys.path.insert(0, '.')
from par.md import parseHtml
from .commands import call, register_command, Command, get_answer, get_input
from optparse import make_option
from . import template
from .utils import log
import shutil
from copy import deepcopy

__author__ = 'limodou'
__author_email__ = 'limodou@gmail.com'
__url__ = 'https://github.com/limodou/parm'
__license__ = 'BSD'
__version__ = '1.4.1'

#import parm project config module
try:
    import conf
except:
    conf = None

def fix_dir(path):
    """
    Check if directory is existed, if not then create it
    """
    _dir = os.path.dirname(path)
    if not os.path.exists(_dir):
        os.makedirs(_dir)
        
class InitCommand(Command):
    name = 'init'
    help = "Init a parm project environment. It'll create a config.py file."
    
    def handle(self, options, global_options, *args):
        from .utils import extract_dirs, pkg, extract_file
        from shutil import copy
        
        if os.path.exists('conf.py'):
            has_conf = True
        else:
            has_conf = False
            
        d = {}
        
        d['project'] = getattr('conf', 'project', 'Parm')
        d['copyright'] = getattr('conf', 'copyright', '2014, Limodou')
        d['version'] = getattr('conf', 'version', __version__)
        d['theme'] = getattr(conf, 'theme', 'semantic')
        d['template_dirs'] = getattr(conf, 'template_dirs', 'templates')
        d['disqus'] = getattr(conf, 'disqus', '')
        d['domain'] = getattr(conf, 'domain', '')
        
        if has_conf:
            create = get_answer("Create config file", quit='q') == 'Y'
        
        if not has_conf or (has_conf and create):
            d['project'] = get_input("Project name [%s]:"%d['project'], default=d['project'])
            d['copyright'] = get_input("Copyright information [%s]:" % d['copyright'], default=d['copyright'])
            d['version'] = get_input("Version [%s]:" % d['version'], default=d['version'])
            d['theme'] = get_input("Choice theme (bootstrap, semantic) [%s]:" % d['theme'], choices=['bootstrap', 'semantic'], default=d['theme'])
            d['disqus'] = get_input("Disqus account name [%s]:" % d['disqus'], default=d['disqus'])
            d['search'] = get_answer("If you want to add search input") == 'Y'
            d['domain'] = get_input("Domain name used for search [%s]:" % d['domain'], default=d['domain'])
            
            if d['theme'] == 'bootstrap':
                d['tag_class'] = """
'table':'table table-bordered',
'pre':'+prettyprint',
"""
            elif d['theme'] == 'semantic':
                d['tag_class'] = """
'table':'ui collapsing celled table segment',
'pre':'+prettyprint',
"""
            
            conf_file = pkg.resource_filename('parm', 'templates/env/conf.py.txt')
            text = template.template_file(conf_file, d).replace('\r\n', '\n')
            f = open('conf.py', 'w')
            f.write(text)
            f.close()
        
        run = False
        if os.path.exists(d['template_dirs']):
            print("Template directory [%s] is already existed! If you've changed them, please deal with manually, otherwise the content will be overwritten." % d['template_dirs'])
            if get_answer("Overwrite template files") == 'Y':
                run = True
        else:
            run = True
        
        if run:
            print('Copy %s to ./%s' % ('theme/%s/templates' % d['theme'], d['template_dirs']))
            extract_dirs('parm', 'templates/theme/%s/templates' % d['theme'], 
                d['template_dirs'])
                
        if get_answer("Copy init files [index.md*]") == 'Y':
            for f in ['index.md', 'introduction.md', 'exclude.txt']:
                if os.path.exists(f):
                    print('%s is already existed, so just skip it' % f)
                else:
                    print('Copy templates/env/%s to ./%s' % (f, f))
                    extract_file('parm', 'templates/env/%s' % f, '.')
        
register_command(InitCommand)

class MakeCommand(Command):
    name = 'make'
    help = "Make parm project. It'll create all markdown files to html files."
    has_options = True
    option_list = (
        make_option('-d', dest='directory', default='html',
            help='Output directory of converted files.'),
    )
    
    r_header = re.compile(r'<h(\d)(.*?)>(.*?)(<a.*?/a>)\s*</h\1>', re.IGNORECASE)
    r_tag = re.compile(r'<.*?>')
    r_id = re.compile(r'id="([^"]*)"')
    
    def handle(self, options, global_options, *args):
        from .utils import extract_dirs, copy_dir, walk_dirs, import_attr
        from .md_ext import new_code_comment, toc, include
        from functools import partial
        from shutil import copy2

        if not conf:
            log.error('Current directory is not a parm project')
            sys.exit(1)
            
        #make output directory
        if not os.path.exists(options.directory):
            print('Make directories [%s]' % options.directory)
            os.makedirs(options.directory)
            
        #get theme config
        theme = getattr(conf, 'theme', 'semantic')
        print('Using theme [%s]' % theme)
        
        #copy static files
        print('Copy %s to %s' % ('theme/%s/static' % theme, os.path.join(options.directory, 'static')))
        extract_dirs('parm', 'templates/theme/%s/static' % theme, 
            os.path.join(options.directory, 'static'))
            
        dst_dir = os.path.normpath(os.path.abspath(options.directory)).replace('\\', '/') + '/'
        
        #process exclude
        if os.path.exists('exclude.txt'):
            _exclude = open('exclude.txt').read().splitlines()
        else:
            _exclude = []
        _exclude.extend([options.directory, conf.template_dirs])
        files = list(walk_dirs('.', exclude=_exclude))
        headers = {}
        relations = {}
        
        #prepare block process handlers
        blocks = {}
        blocks['code-comment'] = new_code_comment
        blocks['toc'] = partial(toc, headers=headers, relations=relations)
        blocks['include'] = include

        #according theme import different blocks
        mod_path = 'par.%s_ext.blocks' % theme
        b = import_attr(mod_path)
        blocks.update(b)
        
        output_files = {}
        template_dirs = conf.template_dirs
        
        while 1:
            if not files:
                break
            
            path = files.pop(0)
            fname, ext = os.path.splitext(path)
            if os.path.isfile(path) and (ext in conf.source_suffix):
                if fname == conf.master_doc and len(files)>0:
                    files.append(path)
                    continue
                
                with open(path) as f:
                    
                    data = {}
                    data['conf'] = conf
                    
                    #process markdown convert
                    data['body'] = parseHtml(f.read(), 
                        '', 
                        conf.tag_class,
                        block_callback=blocks,
                        filename=path)
                    page_nav = relations.get(fname, {})
                    data['prev'] = page_nav.get('prev', {})
                    data['next'] = page_nav.get('next', {})
                    data['relpath'] = '.' * (path.count('/')+1)
                    data['source'] = '<a href="%s/%s">%s</a>' % (data['relpath'], path, conf.download_source)
                    
                    #parse header from text
                    h = headers.setdefault(path, [])
                    title = self.parse_headers(path, data['body'], h)
                    if title:
                        data['title'] = title + ' - ' + conf.project
                    else:
                        if fname != conf.master_doc:
                            print('Error: Heading 1 not found in file %s' % path)
                            continue
                        else:
                            data['title'] = conf.project

                    #convert conf attributes to data
                    for k in dir(conf):
                        if not k.startswith('_'):
                            data[k] = getattr(conf, k)
                       
                    #process template
                    template_file = conf.templates.get(fname, conf.templates.get('*', 'default.html'))
                    hfilename = os.path.join(options.directory, fname + '.html').replace('\\', '/')
                    fix_dir(hfilename)
                    with open(hfilename, 'w') as fh:
                        print('Convert %s to %s' % (path, hfilename))
                        fh.write(template.template_file(template_file, data, dirs=[template_dirs]))
                        copy2(path, os.path.join(options.directory, path))
                    output_files[fname] = hfilename
                    
            else:
                if os.path.isdir(path):
                    dpath = os.path.join(dst_dir, path)
                    if not os.path.exists(dpath):
                        print('Makedir %s' % os.path.join(dst_dir, path))
                        os.makedirs(dpath)
                else:
                    print('Copy %s to %s' % (path, os.path.join(dst_dir, path)))
                    shutil.copy(path, os.path.join(dst_dir, path))
                
        prev_next_template_top = """{{if prev:}}<div class="chapter-prev chapter-top">
    <a prev-chapter href="{{<< prev['link']}}"><i class="icon-arrow-left"></i> {{=prev['title']}}</a>
</div>{{pass}}
{{if next:}}<div class="chapter-next chapter-top">
    <a next-chapter href="{{<< next['link']}}">{{=next['title']}} <i class="icon-arrow-right"></i></a>
</div>{{pass}}"""
        prev_next_template_down = """{{if prev:}}<div class="chapter-prev chapter-down">
    <a prev-chapter href="{{<< prev['link']}}"><i class="icon-arrow-left"></i> {{=prev['title']}}</a>
</div>{{pass}}
{{if next:}}<div class="chapter-next chapter-down">
    <a next-chapter href="{{<< next['link']}}">{{=next['title']}} <i class="icon-arrow-right"></i></a>
</div>{{pass}}"""
        
        for name, f in output_files.items():
            text = open(f).read()
            
            x = relations.get(name, {})
            data = {}
            data['prev'] = x.get('prev', {})
            if data['prev']:
                relpath = '.' * (data['prev']['link'].count('/')+1)
                data['prev']['link'] = relpath + '/' + data['prev']['link']
            data['next'] = x.get('next', {})
            if data['next']:
                relpath = '.' * (data['next']['link'].count('/')+1)
                data['next']['link'] = relpath + '/' + data['next']['link']
            
            prev_next_text_top = template.template(prev_next_template_top, data)
            prev_next_text_down = template.template(prev_next_template_down, data)
            text = text.replace('<!-- prev_next_top -->', prev_next_text_top)
            text = text.replace('<!-- prev_next_down -->', prev_next_text_down)
            with open(f, 'w') as fh:
                fh.write(text)

    def parse_headers(self, filename, text, headers):
        title = None
        for x in MakeCommand.r_header.findall(text):
            fname, ext = os.path.splitext(filename)
            d = {
                'level':int(x[0]), 
                'title':MakeCommand.r_tag.sub('', x[2]),
                'link':'%s.html' % fname,
            }
            _id = MakeCommand.r_id.search(x[1])
            if _id:
                d['id'] = _id.group(1)
            else:
                log.error("Can't find anchor for head line %s:%s" % (filename, d['title']))
                d['id'] = None
                
            headers.append(d)
            if d['level'] == 1:
                title = d['title']
        return title
            
register_command(MakeCommand)

class Rst2MdCommand(Command):
    name = 'rst2md'
    help = ("Convert reStructuredText to Markdown. \n\nThis tool can't convert "
        "everything of rst to markdown very well, so you need to modify the output "
        "files manually, but it's a good start point")
    args = '[rstfile, rstfile...]'
    option_list = (
        make_option('-e', dest='extension', default='.rst',
            help='Extension of the reStructuredText file, default is ".rst".'),
        make_option('-d', dest='directory', default='.',
            help='Output directory of converted files.'),
    )
    
    def handle(self, options, global_options, *args):
        from docutils.core import publish_file
        import glob
        from . import markdown_writer
        from .utils import walk_dirs
        
        source = os.getcwd()
        
        if not os.path.exists(options.directory):
            os.makedirs(options.directory)
            
        if not args:
            files = walk_dirs(source, include_ext=options.extension, file_only=True)
        else:
            files = args
        for f in files:
            nf = os.path.join(options.directory, os.path.splitext(os.path.basename(f))[0] + '.md')
            if global_options.verbose:
                print('Convert %s...' % f)
            publish_file(source_path=f, 
                destination_path=nf,
                writer=markdown_writer.Writer())
        
register_command(Rst2MdCommand)

def main():
    if conf:
        modules = getattr(conf, 'plugins', [])
    else:
        modules = []
    call('parm', __version__, modules)
    
if __name__ == '__main__':
    main()
