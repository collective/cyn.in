"""A testing base class providing some common functionality"""

from Products.PloneTestCase import PloneTestCase
from Products.CMFCore.utils import getToolByName
from Products.WebServerAuth.utils import firstInstanceOfClass
from Products.WebServerAuth.plugin import MultiPlugin

userId = 'fred'


class WebServerAuthTestCase(PloneTestCase.PloneTestCase):
    def _acl_users(self):
        """Return the acl_users folder in the Plone site."""
        return getToolByName(self.portal, 'acl_users')
    
    def _plugin(self):
        """Return the installed multiplugin or, if none is installed, None."""
        return firstInstanceOfClass(self._acl_users(), MultiPlugin)


class MockRequestTestCase(WebServerAuthTestCase):
    def afterSetUp(self):
        def getMockRequest():
            """Return a request that looks like we traversed to the root of the Plone site."""
            old_parents = self.app.REQUEST.get('PARENTS')
            self.app.REQUEST.set('PARENTS', [self.app])  # make clone() work
            request = self.app.REQUEST.clone()
            self.app.REQUEST.set('PARENTS', old_parents)
            
            request.set('PUBLISHED', self.portal)
            request.steps = list(self.portal.getPhysicalPath())
            request.environ['HTTP_X_REMOTE_USER'] = userId
            return request
            
        self.logout()
        
        # Rig the REQUEST that looks like we traversed to the root of the Plone site:
        self.old_request = self.app.REQUEST
        self.app.REQUEST = getMockRequest()
    
    def beforeTearDown(self):
        self.app.REQUEST = self.old_request
