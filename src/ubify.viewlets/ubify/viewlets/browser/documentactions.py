from plone.app.layout.viewlets.content import DocumentActionsViewlet
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

class CyninDocumentActionsViewlet(DocumentActionsViewlet):
    index = ViewPageTemplateFile("document_actions.pt")
