from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone.app.layout.viewlets.common import TableOfContentsViewlet

class TableOfContentsViewletEx(TableOfContentsViewlet):
    index = ViewPageTemplateFile('toc_ex.pt')
