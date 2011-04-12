"""Define a sub-class of ``Five.testbrowser.Browser`` that contains
useful wrappers to write functional test cases for Plone products.

FIXME: OMG, it's horrible, we have got no tests! This code is
useless... blah blah blah...

$Id: plonetestbrowser.py 67788 2008-07-04 08:16:40Z dbaty $
"""

from Products.Five.testbrowser import Browser as BaseBrowser


class Browser(BaseBrowser):
    """A test browser that provides useful wrappers for Plone."""

    def submitForm(self, form_name=None, form_id=None,
                   submit_button_name=None, **kwargs):
        """Submit ``form`` with values given in ``kwargs``.

        FIXME: describe
        """
        if form_id is not None:
            form = self.getForm(id=form_id)
        elif form_name:
            form = self.getForm(name=form_name)
        else:
            raise ValueError('FIXME')
        for name, value in kwargs.items():
            control = form.getControl(name=name)
            control.value = value

        form.submit(name=submit_button_name)


    def loginAsManager(self, url=None, userid='manager', password='manager'):
        """Login to the site with the given credentials."""
        if url is not None:
            self.open(url)
        self.submitForm(form_id='login_form',
                        submit_button_name='submit',
                        __ac_name=userid,
                        __ac_password=password)


    def createItem(self, container, portal_type, **kwargs):
        """Create a new item in ``container``.

        ``kwargs`` can contain field values of the created item. For
        example: ``title``,  ``description``, etc.

        If an argument has no corresponding field, an error is raised.
        """
        url = container.absolute_url()
        url += '/createObject?type_name=%s' % portal_type
        self.open(url)
        self.submitForm(form_name='edit_form',
                        submit_button_name='form_submit', **kwargs)


    def editItem(self, item, **kwargs):
        """Edit ``item``.

        ``kwargs`` can contain field values of the created item. For
        example: ``title``,  ``description``, etc.

        If an argument has no corresponding field, an error is raised.
        """
        url = item.absolute_url()
        url += '/edit'
        self.open(url)
        self.submitForm(form_name='edit_form',
                        submit_button_name='form_submit', **kwargs)


    def doWorkflowTransitionOn(self, transition, item):
        """Do ``transition`` on ``item``."""
        self.open(item.absolute_url())
        ## FIXME: this a cheat
        url = item.absolute_url()
        url += '/content_status_modify?workflow_action=%s' % transition
        self.open(url)
