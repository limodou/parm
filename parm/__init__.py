#! /usr/bin/env python
#coding=utf-8
#
# Author: limodou@gmail.com
# This program is based on pyPEG
#
# license: BSD
#
import os, sys
import re
sys.path.insert(0, '.')
from par.md import parseHtml
from commands import call, register_command, Command, get_answer, get_input
from optparse import make_option
import template
from utils import log

__author__ = 'limodou'
__author_email__ = 'limodou@gmail.com'
__url__ = 'https://github.com/limodou/parm'
__license__ = 'BSD'
__version__ = '0.1'

#import parm project config module
try:
    import conf
except:
    conf = None

class InitCommand(Command):
    name = 'init'
    help = "Init a parm project environment. It'll create a config.py file."
    
    def handle(self, options, global_options, *args):
        from utils import extract_dirs
        
        extract_dirs('parm', 'templates/env', '.')
        if not os.path.exists('static'):
            os.makedirs('static')
            
        d = {}
        
        d['project'] = 'Parm'
        d['copyright'] = '2012, Limodou'
        d['version'] = '1.0'
        config = get_answer("Create config file", quit='q') == 'Y'
        if config:
            d['project'] = get_input("Project name [Parm]:", default=d['project'])
            d['copyright'] = get_input("Copyright information [%s]:" % d['copyright'], default=d['copyright'])
            d['version'] = get_input("Version [%s]:" % d['version'], default=d['version'])
        
        text = template.template_file('conf.py', d).replace('\r\n', '\n')
        f = open('conf.py', 'wb')
        f.write(text)
        f.close()
            
register_command(InitCommand)

class MakeCommand(Command):
    name = 'make'
    help = "Make parm project. It'll create all markdown files to html files."
    has_options = True
    option_list = (
        make_option('-d', dest='directory', default='../html',
            help='Output directory of converted files.'),
    )
    
    r_header = re.compile(r'<h(\d)(.*?)>(.*?)</h\1>', re.IGNORECASE)
    r_tag = re.compile(r'<.*?>')
    r_id = re.compile(r'id="([^"]*)"')
    
    def handle(self, options, global_options, *args):
        from utils import extract_dirs, copy_dir
        from par.bootstrap_ext import blocks
        from md_ext import code_comment, toc
        from functools import partial

        if not conf:
            log.error('Current directory is not a parm project')
            sys.exit(1)
            
        #make output directory
        if not os.path.exists(options.directory):
            print 'Make directories [%s]' % options.directory
            os.makedirs(options.directory)
            
        #copy static files
        print 'Copy default templates/static to %s' % options.directory
        extract_dirs('parm', 'templates/static', 
            os.path.join(options.directory, 'static'))
            
        #compile markdown files
        files = list(os.listdir('.'))
        headers = {}
        relations = {}
        
        #prepare block process handlers
        blocks['code-comment'] = code_comment
        blocks['toc'] = partial(toc, headers=headers, relations=relations)

        output_files = {}
        
        while 1:
            if not files:
                break
            
            path = files.pop(0)
            fname, ext = os.path.splitext(path)
            if os.path.isfile(path) and (ext in conf.source_suffix):
                if fname == conf.master_doc and len(files)>1:
                    files.append(path)
                    continue
                
                with open(path) as f:
                    
                    data = {}
                    
                    #process markdown convert
                    data['body'] = parseHtml(f.read(), 
                        '', 
                        conf.tag_class,
                        block_callback=blocks)
                    page_nav = relations.get(fname, {})
                    data['prev'] = page_nav.get('prev', {})
                    data['next'] = page_nav.get('next', {})
                    
                    #parse header from text
                    h = headers.setdefault(path, [])
                    data['title'] = unicode(self.parse_headers(path, data['body'], h), 'utf8') + ' - ' + conf.project 

                    #convert conf attributes to data
                    for k in dir(conf):
                        if not k.startswith('_'):
                            data[k] = getattr(conf, k)
                       
                    #process template
                    template_file = conf.templates.get(fname, conf.templates.get('*', 'default.html'))
                    hfilename = os.path.join(options.directory, fname + '.html').replace('\\', '/')
                    with open(hfilename, 'wb') as fh:
                        print 'Convert %s to %s' % (path, hfilename)
                        fh.write(template.template_file(template_file, data, dirs=['_build']))
                
                    output_files[fname] = hfilename
                    
            elif os.path.isdir(path) and not path.startswith('_'):
                print 'Copy %s to %s' % (path, options.directory)
                copy_dir(path, os.path.join(options.directory, path))
                
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
            text = open(f, 'rb').read()
            
            x = relations.get(name, {})
            data = {}
            data['prev'] = x.get('prev', {})
            data['next'] = x.get('next', {})
            
            prev_next_text_top = template.template(prev_next_template_top, data)
            prev_next_text_down = template.template(prev_next_template_down, data)
            text = text.replace('<!-- prev_next_top -->', prev_next_text_top)
            text = text.replace('<!-- prev_next_down -->', prev_next_text_down)
            with open(f, 'wb') as fh:
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

def main():
    if conf:
        modules = conf.plugins
    else:
        modules = []
    call('parm', __version__, modules)
    
if __name__ == '__main__':
    main()
