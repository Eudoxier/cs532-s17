#!/usr/bin/env python
# -*- coding: utf-8 -*- #
from __future__ import unicode_literals

AUTHOR = 'Derek Goddeau'
SITENAME = 'CS 432 Web Science'
SITEURL = 'http://datenstrom.gitlab.io/cs532-s17'
SITETITLE = '{}'.format(AUTHOR)
SITESUBTITLE = 'CS 432 Reports'
SITEDESCRIPTION = 'CS 432 Assignments'
SITELOGO = 'images/profile.png'
FAVICON = 'images/favicon.png'
ROBOTS = 'index, follow'
PATH = 'content'
BROWSER_COLOR = '#333333'
PYGMENTS_STYLE = 'monokai'

TIMEZONE = 'America/New_York'
DEFAULT_LANG = 'en'
OG_LOCALE = 'en_US'
LOCALE = 'en_US'

CC_LICENSE = {
    'name': 'Creative Commons Attribution-ShareAlike',
    'version': '4.0',
    'slug': 'by-sa'
}
COPYRIGHT_YEAR = 2017

USE_FOLDER_AS_CATEGORY = False
MAIN_MENU = True
RELATIVE_URLS = True

# Feed generation is usually not desired when developing
FEED_ALL_ATOM = None
CATEGORY_FEED_ATOM = None
TRANSLATION_FEED_ATOM = None
AUTHOR_FEED_ATOM = None
AUTHOR_FEED_RSS = None

#PLUGIN_PATHS = ['pelican-plugins']
#PLUGINS = ['sitemap', 'post_stats']

STATIC_PATHS = ['images', 'pdfs', 'pages']

SITEMAP = {
    'format': 'xml',
    'priorities': {
        'articles': 0.6,
        'indexes': 0.6,
        'pages': 0.5,
    },
    'changefreqs': {
        'articles': 'monthly',
        'indexes': 'daily',
        'pages': 'monthly',
    }
}



# Blogroll
LINKS = (('Assignment One', SITEURL + '/pdfs/assignment-one.pdf'),
         ('Assignment Two', SITEURL + '/pdfs/assignment-two.pdf'))

# Social widget
SOCIAL = (('gitlab', 'https://gitlab.com/datenstrom'),
          ('envelope', 'mailto:dgodd001@odu.edu'),
          ('github', 'https://github.com/Eudoxier'))

DEFAULT_PAGINATION = 10

def sidebar(value):
    if value.startswith('archives') or value.startswith('category'):
        return 'right-sidebar'
    elif value == 'index':
        return 'index'
    else:
        return 'no-sidebar'

JINJA_FILTERS = { 'sidebar' : sidebar }
THEME = 'pelican-themes/Flex'
