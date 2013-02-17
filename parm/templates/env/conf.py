#coding=utf8

"""
This config will be used for parm project settings.
You can change them to fit your needs.
"""

#available plugins
plugins = []

# The suffix of source filenames.
source_suffix = ['.md', '.markdown']

#template setttings
template_dirs = "_build"
templates = {'index':'index.html', '*':'default.html'}

tag_class = {
    'table':'table table-bordered',
    'pre':'prettyprint linenums',
}

# pre code theme css only : sons-of-obsidian, sunburst
# can be found in static/asset directory
pre_css = 'sons-of-obsidian'

# General information about the project.
project = u'{{=project}}'
project_url = './index.html'
copyright = u'{{=copyright}}'

# The short X.Y version.
version = '{{=version}}'

# config menus
# format: ('name', 'caption', 'link')
menus = [
    ('home', 'Home', 'index.html'),
]

# in content footer you can config comment tool just like disque
content_footer = ''

#page footer
footer = """<footer class="footer">
  <div>
    <p>Designed by Limodou, Copyright %s</p>
    <p>CSS framework <a href="https://github.com/twitter/bootstrap">Bootstrap</a>, Markdown parser lib <a href="https://github.com/limodou/par">Par</a> and this page is created by <a href="https://github.com/limodou/parm">Parm</a> tool.</p>
  </div>
</footer>
""" % copyright

# The master toctree document.
master_doc = 'index'

#download source display
download_source = 'View Source'