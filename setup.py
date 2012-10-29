__doc__ = """
=====================
Par 
=====================

:Author: Limodou <limodou@gmail.com>

.. contents:: 

About Parm
----------------

Parm can be used to convert markdown files to  html pages. It'll use par module to parse markdown. 
The features are:

* Topic content page support
* Bootstrap 2.1.1 css framework based

Requirement
----------------

* par https://github.com/limodou/par

Installation
----------------

```
pip install par
pip install parm
```

Usage
-------------

```
parm --help
parm --version
parm -d output_path
```

License
------------

Parm is released under BSD license. 

"""

from setuptools import setup
import parm

setup(name='parm',
    version=parm.__version__,
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
    ],
    packages = ['parm'],
    platforms = 'any',
    keywords='markdown convertor',
    author=parm.__author__,
    author_email=parm.__author_email__,
    url=parm.__url__,
    license=parm.__license__,
    include_package_data=True,
    zip_safe=False,
    entry_points = {
        'console_scripts': [
            'parm = parm:main',
        ],
    },
)
