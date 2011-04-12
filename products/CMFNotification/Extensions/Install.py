"""Install method.

$Id: Install.py 67087 2008-06-21 16:10:26Z dbaty $
"""

from StringIO import StringIO

from zope.component import getUtility
from zope.component import getMultiAdapter

from Products.CMFCore.utils import getToolByName

from plone.portlets.interfaces import IPortletManager
from plone.portlets.interfaces import IPortletAssignmentMapping

from Products.CMFNotification.config import GLOBALS
from Products.CMFNotification.config import LAYER_NAME
from Products.CMFNotification.config import PORTLET_NAME
from Products.CMFNotification.config import PROJECT_NAME
from Products.CMFNotification.exportimport import addPermissions
from Products.CMFNotification.NotificationTool import ID as TOOL_ID


def install(context):
    """Install CMFNotification.

    Most of the job is done by a Generic Setup profile.
    """
    out = StringIO()
    
    ## I do not know how (and if it is possible) to define that an
    ## import step is a dependency of the 'rolemap' step.
    addPermissions(context)

    ## Import GenericSetup default profile
    setup_tool = getToolByName(context, 'portal_setup')
    setup_tool.runAllImportStepsFromProfile('profile-Products.CMFNotification:default')

    print >> out, "Successfully installed %s." % PROJECT_NAME
    return out.getvalue()


def uninstall(context):
    """Uninstall CMFNotification."""
    portal = getToolByName(context, 'portal_url').getPortalObject()
    
    ## Remove tool
    tool = getToolByName(portal, TOOL_ID, None)
    #if tool is not None:
    #    portal.manage_delObjects([TOOL_ID])

    ## Remove skin layer
    skins_tool = getToolByName(portal, 'portal_skins')
    selections = skins_tool._getSelections()
    for skin, layers in selections.items():
        layers = layers.split(',')
        if LAYER_NAME in layers:
            layers.remove(LAYER_NAME)
        layers = ','.join(layers)
        selections[skin] = layers

    ## Remove portlet
    rightColumn = getUtility(IPortletManager,
                             name=u'plone.rightcolumn',
                             context=portal)
    right = getMultiAdapter((portal, rightColumn),
                            IPortletAssignmentMapping,
                            context=portal)
    if PORTLET_NAME in right:
        del right[PORTLET_NAME]
        
    ## Remove portlet
    leftColumn = getUtility(IPortletManager,
                             name=u'plone.leftcolumn',
                             context=portal)
    left = getMultiAdapter((portal, leftColumn),
                            IPortletAssignmentMapping,
                            context=portal)
    if PORTLET_NAME in left:
        del left[PORTLET_NAME]

    ## Remove configlet
    panel = getToolByName(portal, 'portal_controlpanel')
    if panel is not None:
        panel.unregisterConfiglet('cmfnotification_configuration')
