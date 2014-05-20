from __future__ import print_function
from future.builtins import str
from future import standard_library
standard_library.install_hooks()
from future.builtins import object
import os, sys
import re
import logging
import pickle
import inspect

log = logging

def safe_import(path):
    module = path.split('.')
    g = __import__(module[0], fromlist=['*'])
    s = [module[0]]
    for i in module[1:]:
        mod = g
        if hasattr(mod, i):
            g = getattr(mod, i)
        else:
            s.append(i)
            g = __import__('.'.join(s), fromlist=['*'])
    return mod, g
        
def import_mod_attr(path):
    """
    Import string format module, e.g. 'uliweb.orm' or an object
    return module object and object
    """
    if isinstance(path, str):
        module, func = path.rsplit('.', 1)
        mod = __import__(module, fromlist=['*'])
        f = getattr(mod, func)
    else:
        f = path
        mod = inspect.getmodule(path)
    return mod, f

def import_attr(func):
    mod, f = import_mod_attr(func)
    return f

def myimport(module):
    mod = __import__(module, fromlist=['*'])
    return mod

def install(packages):
    from pkg_resources import load_entry_point
    
    load = load_entry_point('setuptools', 'console_scripts', 'easy_install')
    load(packages)

class MyPkg(object):
    @staticmethod
    def resource_filename(module, path):
        mod = myimport(module)
        p = os.path.dirname(mod.__file__)
        if path:
            return os.path.join(p, path)
        else:
            return p
    
    @staticmethod
    def resource_listdir(module, path):
        d = MyPkg.resource_filename(module, path)
        return os.listdir(d)
    
    @staticmethod
    def resource_isdir(module, path):
        d = MyPkg.resource_filename(module, path)
        return os.path.isdir(d)

try:
    import pkg_resources as pkg
except:
    pkg = MyPkg

def extract_file(module, path, dist, verbose=False, replace=True):
    outf = os.path.join(dist, os.path.basename(path))
#    d = pkg.get_distribution(module)
#    if d.has_metadata('zip-safe'):
#        f = open(outf, 'wb')
#        f.write(pkg.resource_string(module, path))
#        f.close()
#        if verbose:
#            print 'Info : Extract %s/%s to %s' % (module, path, outf)
#    else:
    import shutil

    inf = pkg.resource_filename(module, path)
    sfile = os.path.basename(inf)
    if os.path.isdir(dist):
        dfile = os.path.join(dist, sfile)
    else:
        dfile = dist
    f = os.path.exists(dfile)
    if replace or not f:
        shutil.copy2(inf, dfile)
        if verbose:
            print('Copy %s to %s' % (inf, dfile))
  
def extract_dirs(mod, path, dst, verbose=False, exclude=None, exclude_ext=None, recursion=True, replace=True):
    """
    mod name
    path mod path
    dst output directory
    resursion True will extract all sub module of mod
    """
    default_exclude = ['.svn', '_svn', '.git']
    default_exclude_ext = ['.pyc', '.pyo', '.bak', '.tmp']
    exclude = exclude or []
    exclude_ext = exclude_ext or []
#    log = logging.getLogger('uliweb')
    if not os.path.exists(dst):
        os.makedirs(dst)
        if verbose:
            print('Make directory %s' % dst)
    for r in pkg.resource_listdir(mod, path):
        if r in exclude or r in default_exclude:
            continue
        fpath = os.path.join(path, r)
        if pkg.resource_isdir(mod, fpath):
            if recursion:
                extract_dirs(mod, fpath, os.path.join(dst, r), verbose, exclude, exclude_ext, recursion, replace)
        else:
            ext = os.path.splitext(fpath)[1]
            if ext in exclude_ext or ext in default_exclude_ext:
                continue
            extract_file(mod, fpath, dst, verbose, replace)

def match(f, patterns):
    from fnmatch import fnmatch
    
    flag = False
    for x in patterns:
        if fnmatch(f, x):
            return True
        
def walk_dirs(path, include=None, include_ext=None, exclude=None, 
        exclude_ext=None, recursion=True, file_only=False):
    """
    path directory path
    resursion True will extract all sub module of mod
    """
    default_exclude = ['.svn', '_svn', '.git']
    default_exclude_ext = ['.pyc', '.pyo', '.bak', '.tmp']
    exclude = exclude or []
    exclude_ext = exclude_ext or []
    include_ext = include_ext or []
    include = include or []

    if not os.path.exists(path):
        raise StopIteration
    
    for r in os.listdir(path):
        if match(r, exclude) or r in default_exclude:
            continue
        if include and r not in include:
            continue
        fpath = os.path.join(path, r)
        if os.path.isdir(fpath):
            if not file_only:
                yield os.path.normpath(fpath).replace('\\', '/')
            if recursion:
                for f in walk_dirs(fpath, include, include_ext, exclude, 
                    exclude_ext, recursion, file_only):
                    yield os.path.normpath(f).replace('\\', '/')
        else:
            ext = os.path.splitext(fpath)[1]
            if ext in exclude_ext or ext in default_exclude_ext:
                continue
            if include_ext and ext not in include_ext:
                continue
            yield os.path.normpath(fpath).replace('\\', '/')

def copy_dir(src, dst, verbose=False, check=False, processor=None):
    import shutil

#    log = logging.getLogger('uliweb')

    def _md5(filename):
        try:
            import hashlib
            a = hashlib.md5()
        except ImportError:
            import md5
            a = md5.new()
            
        a.update(file(filename, 'rb').read())
        return a.digest()
    
    if not os.path.exists(dst):
        os.makedirs(dst)

    if verbose:
        print("Processing %s" % src)
        
    for r in os.listdir(src):
        if r in ['.svn', '_svn', '.git']:
            continue
        fpath = os.path.join(src, r)
        
        if os.path.isdir(fpath):
            if os.path.abspath(fpath) != os.path.abspath(dst):
                copy_dir(fpath, os.path.join(dst, r), verbose, check, processor)
            else:
                continue
        else:
            ext = os.path.splitext(fpath)[1]
            if ext in ['.pyc', '.pyo', '.bak', '.tmp']:
                continue
            df = os.path.join(dst, r)
            if check:
                if os.path.exists(df):
                    a = _md5(fpath)
                    b = _md5(df)
                    if a != b:
                        print("Error: Target file %s is already existed, and "
                            "it not same as source one %s, so copy failed" % (fpath, dst))
                else:
                    if processor:
                        if processor(fpath, dst, df):
                            continue
                    shutil.copy2(fpath, dst)
                    if verbose:
                        print("Copy %s to %s" % (fpath, dst))
                    
            else:
                if processor:
                    if processor(fpath, dst, df):
                        continue
                shutil.copy2(fpath, dst)
                if verbose:
                    print("Copy %s to %s" % (fpath, dst))

def copy_dir_with_check(dirs, dst, verbose=False, check=True, processor=None):
#    log = logging.getLogger('uliweb')

    for d in dirs:
        if not os.path.exists(d):
            continue

        copy_dir(d, dst, verbose, check, processor)

def is_pyfile_exist(dir, pymodule):
    path = os.path.join(dir, '%s.py' % pymodule)
    if not os.path.exists(path):
        path = os.path.join(dir, '%s.pyc' % pymodule)
        if not os.path.exists(path):
            path = os.path.join(dir, '%s.pyo' % pymodule)
            if not os.path.exists(path):
                return False
    return True
    
def wraps(src):
    def _f(des):
        def f(*args, **kwargs):
            from uliweb import application
            if application:
                env = application.get_view_env()
                for k, v in env.items():
                    src.__globals__[k] = v
                
                src.__globals__['env'] = env
            return des(*args, **kwargs)
        
        f.__name__ = src.__name__
        f.__globals__.update(src.__globals__)
        f.__doc__ = src.__doc__
        f.__module__ = src.__module__
        f.__dict__.update(src.__dict__)
        return f
    
    return _f

def timeit(func):
    log = logging.getLogger('uliweb.app')
    import time
    @wraps(func)
    def f(*args, **kwargs):
        begin = time.time()
        ret = func(*args, **kwargs)
        end = time.time()
        print(("%s.%s [%s]s" % (func.__module__, func.__name__, end-begin)))
        return ret
    return f

def get_var(key):
    def f():
        from uliweb import settings
        
        return settings.get_var(key)
    return f

def get_choice(choices, value, default=None):
    if callable(choices):
        choices = choices()
    return dict(choices).get(value, default)

def simple_value(v, encoding='utf-8', none=False):
    import datetime
    import decimal
    
    if callable(v):
        v = v()
    if isinstance(v, datetime.datetime):
        return v.strftime('%Y-%m-%d %H:%M:%S')
    elif isinstance(v, datetime.date):
        return v.strftime('%Y-%m-%d')
    elif isinstance(v, datetime.time):
        return v.strftime('%H:%M:%S')
    elif isinstance(v, decimal.Decimal):
        return str(v)
    elif isinstance(v, str):
        return v.encode(encoding)
    elif isinstance(v, (tuple, list)):
        s = []
        for x in v:
            s.append(simple_value(x, encoding, none))
        return s
    elif isinstance(v, dict):
        d = {}
        for k, v in v.items():
            d[simple_value(k)] = simple_value(v, encoding, none)
        return d
    elif v is None:
        if none:
            return v
        else:
            return ''
    else:
        return v
    
def str_value(v, encoding='utf-8', bool_int=True, none='NULL'):
    import datetime
    import decimal
    
    if callable(v):
        v = v()
    if isinstance(v, datetime.datetime):
        return v.strftime('%Y-%m-%d %H:%M:%S')
    elif isinstance(v, datetime.date):
        return v.strftime('%Y-%m-%d')
    elif isinstance(v, datetime.time):
        return v.strftime('%H:%M:%S')
    elif isinstance(v, decimal.Decimal):
        return str(v)
    elif isinstance(v, str):
        return v.encode(encoding)
    elif v is None:
        return none
    elif isinstance(v, bool):
        if bool_int:
            if v:
                return '1'
            else:
                return '0'
        else:
            return str(v)
    else:
        return str(v)

__caches__ = {}
def cache_get(key, func, _type='default'):
    global __caches__
    v = __caches__.setdefault(_type, {})
    if key in v and v[key]:
        return v[key]
    else:
        v[key] = func(key)
        return v[key]
    
def norm_path(path):
    return os.path.normcase(os.path.abspath(path))

r_expand_path = re.compile('\$\{(\w+)\}')
def expand_path(path):
    """
    Auto search some variables defined in path string, such as:
        ${PROJECT}/files
        ${app_name}/files
    for ${PROJECT} will be replaced with uliweb application apps_dir directory
    and others will be treated as a normal python package, so uliweb will
    use pkg_resources to get the path of the package
    """
    from uliweb import application
    
    def replace(m):
        txt = m.groups()[0]
        if txt == 'PROJECT':
            return application.apps_dir
        else:
            return pkg.resource_filename(txt, '')
    return re.sub(r_expand_path, replace, path)

def date_in(d, dates):
    """
    compare if d in dates. dates should be a tuple or a list, for example:
        date_in(d, [d1, d2])
    and this function will execute:
        d1 <= d <= d2
    and if d is None, then return False
    """
    if not d:
        return False
    return dates[0] <= d <= dates[1]

class Serial(object):
    @classmethod
    def load(self, s):
        return pickle.loads(s)
    
    @classmethod
    def dump(self, v):
        return pickle.dumps(v, pickle.HIGHEST_PROTOCOL)

import future.moves.urllib.parse as urllib_parse
class QueryString(object):
    def __init__(self, url):
        self.url = url
        self.scheme, self.netloc, self.script_root, qs, self.anchor = self.parse()
        self.qs = urllib_parse.parse_qs(qs, True)
        
    def parse(self):
        return urllib_parse.urlsplit(self.url)
    
    def __getitem__(self, name):
        return self.qs.get(name, [])
    
    def __setitem__(self, name, value):
        self.qs[name] = [value]
    
    def set(self, name, value, replace=False):
        v = self.qs.setdefault(name, [])
        if replace:
            self.qs[name] = [value]
        else:
            v.append(value)
        return self

    def __str__(self):
        import urllib.request, urllib.parse, urllib.error
        
        qs = urllib.parse.urlencode(self.qs, True)
        return urllib_parse.urlunsplit((self.scheme, self.netloc, self.script_root, qs, self.anchor))
    
def query_string(url, replace=True, **kwargs):
    q = QueryString(url)
    for k, v in kwargs.items():
        q.set(k, v, replace)
    return str(q)

def camel_to_(s):
    """
    Convert CamelCase to camel_case
    """
    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', s)
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()
    
def get_uuid(type=4):
    """
    Get uuid value
    """
    import uuid
    
    name = 'uuid'+str(type)
    u = getattr(uuid, name)
    return u().hex

def pretty_dict(d, leading=' ', newline='\n', indent=0, tabstop=4, process=None):
    """
    Output pretty formatted dict, for example:
        
        d = {"a":"b",
            "c":{
                "d":"e",
                "f":"g",
                }
            }
        
    will output:
        
        a : 'b'
        c : 
            d : 'e'
            f : 'g'
        
    """
    for k, v in d.items():
        if process:
            k, v = process(k, v)
        if isinstance(v, dict):
            yield '%s%s : %s' % (indent*tabstop*leading, k, newline)
            for x in pretty_dict(v, leading=leading, newline=newline, indent=indent+1, tabstop=tabstop):
                yield x
            continue
        yield '%s%s : %s%s' % (indent*tabstop*leading, k, simple_value(v), newline)


#if __name__ == '__main__':
#    log.info('Info: info')
#    try:
#        1/0
#    except:
#        log.exception('1/0')
