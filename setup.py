__doc__ = """
=====================
Parm 
=====================

:Author: Limodou <limodou@gmail.com>

About Parm
----------------

Parm can be used to convert markdown files to  html pages. It'll use par module 
to parse markdown.
 
The features are:

* Topic content page support
* Bootstrap theme(2.1.1 css framework based)
* Semantic-UI theme

Requirement
----------------

* par https://github.com/limodou/par

Installation
----------------

::
    
    pip install parm

Usage
-------------

::
    
    parm --help
    parm --version
    parm init
    parm make [-d directory]
    parm rst2md

License
------------

Parm is released under BSD license. 

"""

from setuptools import setup
from setuptools.command import build_py as b
import os

#remove build and dist directory
import shutil

def copy_dir(self, package, src, dst):
    self.mkpath(dst)
    for r in os.listdir(src):
        if r in ['.svn', '_svn']:
            continue
        fpath = os.path.join(src, r)
        if os.path.isdir(fpath):
            copy_dir(self, package + '.' + r, fpath, os.path.join(dst, r))
        else:
            ext = os.path.splitext(fpath)[1]
            if ext in ['.pyc', '.pyo', '.bak', '.tmp']:
                continue
            target = os.path.join(dst, r)
            self.copy_file(fpath, target)

def find_dir(self, package, src):
    for r in os.listdir(src):
        if r in ['.svn', '_svn']:
            continue
        fpath = os.path.join(src, r)
        if os.path.isdir(fpath):
            for f in find_dir(self, package + '.' + r, fpath):
                yield f
        else:
            ext = os.path.splitext(fpath)[1]
            if ext in ['.pyc', '.pyo', '.bak', '.tmp']:
                continue
            yield fpath

def build_package_data(self):
    for package in self.packages or ():
        src_dir = self.get_package_dir(package)
        build_dir = os.path.join(*([self.build_lib] + package.split('.')))
        copy_dir(self, package, src_dir, build_dir)
setattr(b.build_py, 'build_package_data', build_package_data)

def get_source_files(self):
    filenames = []
    for package in self.packages or ():
        src_dir = self.get_package_dir(package)
        filenames.extend(list(find_dir(self, package, src_dir)))
    return filenames
setattr(b.build_py, 'get_source_files', get_source_files)

setup(name='parm',
    version='1.4.1',
    description="Markdown to html convertor tool",
    long_description=__doc__,
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: BSD License",
        "Programming Language :: Python",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 2.6",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3.3",
        "Programming Language :: Python :: 3.4",
    ],
    packages = ['parm'],
    platforms = 'any',
    keywords='markdown convertor',
    author='limodou',
    author_email='limodou@gmail.com',
    url='https://github.com/limodou/parm',
    license='BSD',
    include_package_data=True,
    zip_safe=False,
    entry_points = {
        'console_scripts': [
            'parm = parm:main',
        ],
    },
    install_requires=['par']
)
