from zope.component import Interface, adapts
from zope.interface import implements

from Products.ATContentTypes.interface.folder import IATFolder
from interfaces import IXMLRPCFolder



class XMLRPCFolder:
    """Implements IXMLRPCFolder"""

    implements(IXMLRPCFolder)
    adapts(IATFolder)
    
    def ListFolderContents(self):
        """Returns list of objectIds"""
        
        return self.context.objectIds