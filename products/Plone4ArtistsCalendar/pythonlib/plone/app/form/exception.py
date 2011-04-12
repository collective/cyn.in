__docformat__ = 'restructuredtext'

from cgi import escape

from zope.interface import implements
from zope.i18n import translate

from zope.app.form.interfaces import IWidgetInputError
from zope.app.form.browser.interfaces import IWidgetInputErrorView

class WidgetInputErrorView(object):
    """A widget error view that hardcodes no html"""
    implements(IWidgetInputErrorView)

    __used_for__ = IWidgetInputError

    def __init__(self, context, request):
        self.context, self.request = context, request

    def snippet(self):
        """Convert a widget input error to an html snippet

        >>> from zope.app.form.interfaces import WidgetInputError
        >>> class TooSmallError(object):
        ...     def doc(self):
        ...         return "Foo input < 1"
        >>> err = WidgetInputError("foo", "Foo", TooSmallError())
        >>> view = WidgetInputErrorView(err, None)
        >>> view.snippet()
        u'Foo input &lt; 1'

        The only method that IWidgetInputError promises to implement is
        `doc()`. Therefore, other implementations of the interface should also
        work.

        >>> from zope.app.form.interfaces import ConversionError
        >>> err = ConversionError('Could not convert to float.')
        >>> view = WidgetInputErrorView(err, None)
        >>> view.snippet()
        u'Could not convert to float.'
        """
        message = self.context.doc()
        translated = translate(message, context=self.request, default=message)
        return u'%s' % escape(translated)
