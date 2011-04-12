from Acquisition import aq_inner, aq_base
from zope import schema
from zope.formlib import form
from zope.app.form.browser.textwidgets import TextAreaWidget
from Products.Five.formlib.formbase import PageDisplayForm, PageForm
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.CMFCore import utils as cmfutils
from Products.Archetypes import Field, Widget
from Products.ATContentTypes.content import document

class RichTextEditWidget(BrowserView, TextAreaWidget):
    """A Zope 3 based formlib widget that exposes whatever rich text
    editor is configured inside Plone.
    """

    template = ViewPageTemplateFile('atwidget.pt')

    def __init__(self, *args, **kwargs):
        BrowserView.__init__(self, *args, **kwargs)
        TextAreaWidget.__init__(self, *args, **kwargs)

    def content_context(self):
        current = aq_inner(self.context.context)
        content_context = None
        for x in range(100):
            if hasattr(current, '__of__'):
                content_context = current
                break
            if hasattr(current, 'context'):
                current = current.context
            else:
                break
        return content_context

    def __call__(self):
        self.context.REQUEST = self.request
        if not 'body' in self.request.form:
            self.request.form['body'] = self.context.get(self.context.context)
        template = aq_base(self.template)
        widget = aq_base(self)
        content_context = self.content_context()

        template = template.__of__(widget.__of__(content_context))
        return template()

    def hasInput(self):
        return 'body' in self.request.form

    def getInputValue(self):
        return self.request.form.get('body', None)

form_fields = form.FormFields(
    schema.Text(__name__='simpletext',
                title=u'Simple Text',
                required=False),
    schema.Text(__name__='richtext',
                title=u'Rich Text',
                required=False),
    )

class TestEditFieldsView(PageForm):
    """
    """

    label = u'Test Fields'
    form_fields = form_fields
    form_fields['richtext'].custom_widget = RichTextEditWidget

    @form.action('Save')
    def handle_save_action(self, action, data):
        pass

class TestDisplayFieldsView(PageDisplayForm):
    """
    """

    label = u'Test Fields'
    form_fields = form_fields

    actions = ()
