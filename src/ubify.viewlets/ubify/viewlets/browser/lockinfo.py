from plone.locking.browser.info import LockInfoViewlet
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

class CyninLockInfoViewlet(LockInfoViewlet):
    """This is a viewlet which is not hooked up anywhere. It is referenced
    from plone.app.layout. We do it this way to avoid having the  lower-level
    plone.locking depend on these packages, whilst still providing
    an implementation of the info box in a single place.
    """
    template = ViewPageTemplateFile('lockinfo.pt')
