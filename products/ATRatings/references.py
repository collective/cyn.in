from Products.Archetypes.ReferenceEngine import Reference
from Products.CMFCore.utils import getToolByName

class RatingsReference(Reference):
    def beforeSourceDeleteInformTarget(self):
        object = self.getSourceObject()        
        if hasattr(object,'UID'):
            uid = object.UID()
            ratings_tool = getToolByName(self, 'portal_ratings')
            ratings_tool._deleteRatingsFor(uid)
