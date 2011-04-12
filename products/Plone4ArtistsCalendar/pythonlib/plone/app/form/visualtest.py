from zope import interface, schema
from zope.formlib import form

class ITestSchema(interface.Interface):
    foo = schema.TextLine(title=u'Foo',
                          description=u'Some Random Description')
    bar = schema.Bool(title=u'Bar')

class TestForm(form.FormBase):
    """foo
    """
    
    form_fields = form.FormFields(ITestSchema)
    actions = ()
