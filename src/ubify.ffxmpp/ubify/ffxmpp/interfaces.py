from zope.component import Interface, adapts
from zope.interface import implements

class IFFXMPPSupport(Interface):
    """Interface to the Firefox support XMPP library
    """
    def sayhello():
        """Returns a string with Hello
        """
    def getXMPPServerInfo(self):
        """Returns connection information for calling user"""