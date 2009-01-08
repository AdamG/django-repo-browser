"""Integration objects"""

try:
    import pygments
except ImportError:
    pygments = None


class Diff(object):
    "A diff object, to encapulate support for syntax highlighting"

    def __init__(self, text):
        self.text = text

    def __unicode__(self):
        return self.display

    def __repr__(self):
        return "<repo_browser.Diff at %s>" % hex(id(self))

    @property
    def display(self):
        if pygments is not None:
            return self.highlighted
        return self.text

    @property
    def highlighted(self):
        from django.utils.safestring import mark_safe
        from pygments import highlight
        from pygments.formatters import HtmlFormatter
        from pygments.lexers import DiffLexer

        return mark_safe(highlight(self.text, DiffLexer(), HtmlFormatter()))

