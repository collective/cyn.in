from zope.interface import implements
from zope.viewlet.interfaces import IViewlet

from Acquisition import aq_base
from Products.CMFCore.utils import getToolByName
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ZopeTwoPageTemplateFile
from plone.app.i18n.locales.browser.selector import LanguageSelector as BaseClass

class UbifyLanguageSelector(BaseClass):
    """Language selector."""
    implements(IViewlet)

    render = ZopeTwoPageTemplateFile('languageselector.pt')

