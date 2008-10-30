About django-repo-browser
=========================

This projects aims to provide a portable Django app for browsing code
repositories.

DVCSs are the first target backends - Mercurial, Git, and Bazaar - but
I'd like to have Subversion and CVS at some point as well.


Installation
============

#. Put the directory containing the ``repo_browser`` package on your
   Python path, or symlink it into ``site-packages/``

#. Make sure you have ``base.html`` template which exposes a ``styles``
   block, a ``scripts`` block, and a ``content`` block.

#. Symlink ``media/repo_browser.css`` and ``media/repo_browser.js`` to
   your `MEDIA_ROOT`

#. Add ``url(r'^repos/', include('repo_browser.urls')),`` to your
   ``urls.py``
