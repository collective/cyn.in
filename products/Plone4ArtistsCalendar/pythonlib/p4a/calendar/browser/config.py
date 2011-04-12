from zope.formlib import form
from Products.Five.formlib import formbase
from p4a.calendar import interfaces

class ConfigView(formbase.PageEditForm):
    """Calendar configuration.
    """

    form_fields = form.FormFields(interfaces.ICalendarConfig)
