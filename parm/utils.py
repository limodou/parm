from __future__ import print_function
from ._compat import string_types
import os
import re
import logging
import inspect
import datetime
import decimal


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
    if isinstance(path, string_types):
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
            
        a.update(open(filename, 'rb').read())
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

ESCAPE = re.compile(r'[\x00-\x1f\\"\b\f\n\r\t]')
ESCAPE_DCT = {
    '\\': '\\\\',
    '"': '\\"',
    '\b': '\\b',
    '\f': '\\f',
    '\n': '\\n',
    '\r': '\\r',
    '\t': '\\t',
}
for i in range(0x20):
    ESCAPE_DCT.setdefault(chr(i), '\\u{0:04x}'.format(i))

def encode_basestring(s):
    """Return a JSON representation of a Python string

    """
    def replace(match):
        return ESCAPE_DCT[match.group(0)]
    return '"' + ESCAPE.sub(replace, s) + '"'

def encode_unicode(s):
    """Return a JSON representation of a Python unicode

    """
    return '"' + s.encode('unicode_escape') + '"'

def simple_value(v):
    from uliweb.i18n.lazystr import LazyString

    if callable(v):
        v = v()
    if isinstance(v, LazyString) or isinstance(v, decimal.Decimal) or isinstance(v, datetime.datetime):
        return str(v)
    else:
        return v

class JSONEncoder(object):
    def __init__(self, encoding='utf-8', unicode=False, default=None):
        self.encoding = encoding
        self.unicode = unicode
        self.default = default

    def iterencode(self, obj, key=False):
        if self.default:
            x = self.default(obj)
            obj = x
        if isinstance(obj, str):
            if self.unicode:
                yield encode_unicode(unicode(obj, self.encoding))
            else:
                yield encode_basestring(obj)
        elif isinstance(obj, unicode):
            if self.unicode:
                yield encode_unicode(obj)
            else:
                yield encode_basestring(obj.encode(self.encoding))
        elif obj is None:
            yield 'null'
        elif obj is True:
            yield 'true'
        elif obj is False:
            yield 'false'
        elif isinstance(obj, (int, long)):
            if key:
                yield '"' + str(obj) + '"'
            else:
                yield str(obj)
        elif isinstance(obj, float):
            if key:
                yield '"' + str(obj) + '"'
            else:
                yield str(obj)
        elif isinstance(obj, (list, tuple)):
            yield '['
            first = True
            for x in obj:
                if not first:
                    yield ','
                for y in self.iterencode(x):
                    yield y
                first = False
            yield ']'
        elif isinstance(obj, dict):
            yield '{'
            first = True
            for k, v in obj.iteritems():
                if not first:
                    yield ','
                for x in self.iterencode(k, key=True):
                    yield x
                yield ':'
                for y in self.iterencode(v):
                    yield y
                first = False
            yield '}'
        elif isinstance(obj, decimal.Decimal):
            yield str(obj)
        elif isinstance(obj, datetime.datetime):
            yield '"' + obj.strftime('%Y-%m-%d %H:%M:%S') + '"'
        elif isinstance(obj, datetime.date):
            yield '"' + obj.strftime('%Y-%m-%d') + '"'
        elif isinstance(obj, datetime.time):
            yield '"' + obj.strftime('%H:%M:%S') + '"'
        else:
            yield encode_basestring(str(obj))

    def encode(self, obj):
        return ''.join(self.iterencode(obj))

def json_dumps(obj, unicode=False, **kwargs):
    return JSONEncoder(unicode=unicode, default=simple_value, **kwargs).encode(obj)

