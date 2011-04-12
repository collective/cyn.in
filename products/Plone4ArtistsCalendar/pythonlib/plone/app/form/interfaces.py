from zope.interface import Attribute
from zope.formlib.interfaces import IPageForm
from zope.formlib.interfaces import ISubPageForm

class IPlonePageForm(IPageForm):
    """A page form with a couple extra attributes"""
    description = Attribute("A longer description to display on the form")
    form_name = Attribute("A label to apply to the fieldset")

class IPloneSubPageForm(ISubPageForm):
    """A page form with a couple extra attributes"""
    description = Attribute("A longer description to display on the form")
    form_name = Attribute("A label to apply to the fieldset")
