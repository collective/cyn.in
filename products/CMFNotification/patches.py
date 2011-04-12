"""Define CMFNotification patches for CMFCore to call appropriated
handlers when specific events occur.

$Id: patches.py 53736 2007-11-13 13:29:56Z dbaty $
"""

from Products.CMFCore.utils import getToolByName

from NotificationTool import ID, LOG


## FIXME: PAS does fire events, we should use them to replace these
## monkey-patches: see "PluggableAuthService/interfaces/events.py".


######### CMFCore.RegistrationTool patch ########################
def afterAdd(self, member, id, password, properties):
    """Call the original method and also CMFNotification handler."""
    self._cmf_notification_orig_afterAdd(member, id, password, properties)
    ntool = getToolByName(self, ID, None)
    if ntool is not None:
        ntool.onMemberRegistration(member, properties)

from Products.CMFCore.RegistrationTool import RegistrationTool
RegistrationTool._cmf_notification_orig_afterAdd = RegistrationTool.afterAdd
RegistrationTool.afterAdd = afterAdd
LOG.info('Monkey-patched CMFCore.RegistrationTool')
######### End of CMFCore.RegistrationTool patch #################


######### CMFCore.MemberDataTool patch ##########################
def notifyMemberModified(self):
    """Call the original method and also CMFNotification handler."""
    self._cmf_notification_orig_notifyModified()
    ntool = getToolByName(self, ID, None)
    if ntool is not None:
        membership = getToolByName(self, 'portal_membership')
        member = membership.getMemberById(self.getId())
        ntool.onMemberModification(member)

from Products.CMFCore.MemberDataTool import MemberData
MemberData._cmf_notification_orig_notifyModified = MemberData.notifyModified
MemberData.notifyModified = notifyMemberModified
LOG.info('Monkey-patched CMFCore.MemberDataTool')
######### End of CMFCore.MemberDataTool patch ###################
