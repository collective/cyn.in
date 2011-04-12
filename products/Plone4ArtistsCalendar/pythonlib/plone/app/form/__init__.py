from Products.Five.browser import pagetemplatefile
from plone.app.form._named import named_template_adapter
from plone.app.form import _patches
from zope.formlib import namedtemplate, interfaces
from zope import i18n

_patches.apply_formlib_request_locale_patch()
_patches.apply_formlib_update_patch()

@namedtemplate.implementation(interfaces.IAction)
def render_submit_button(self):
    """A custom version of the submit button that uses plone's context class"""
    if not self.available():
        return ''
    label = self.label
    if isinstance(label, (i18n.Message, i18n.MessageID)):
        label = i18n.translate(self.label, context=self.form.request)
    return ('<input type="submit" id="%s" name="%s" value="%s"'
            ' class="context" />' %
            (self.__name__, self.__name__, label)
            )

__all__ = ('named_template_adapter', 'default_named_template')

_template = pagetemplatefile.ViewPageTemplateFile('pageform.pt')
default_named_template_adapter = named_template_adapter(_template)

_subpage_template = pagetemplatefile.ViewPageTemplateFile('subpageform.pt')
default_subpage_template = named_template_adapter(_subpage_template)
