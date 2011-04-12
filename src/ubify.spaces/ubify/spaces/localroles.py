###############################################################################
#cyn.in is an open source Collaborative Knowledge Management Appliance that 
#enables teams to seamlessly work together on files, documents and content in 
#a secure central environment.
#
#cyn.in v2 an open source appliance is distributed under the GPL v3 license 
#along with commercial support options.
#
#cyn.in is a Cynapse Invention.
#
#Copyright (C) 2008 Cynapse India Pvt. Ltd.
#
#This program is free software: you can redistribute it and/or modify it under
#the terms of the GNU General Public License as published by the Free Software 
#Foundation, either version 3 of the License, or any later version and observe 
#the Additional Terms applicable to this program and must display appropriate 
#legal notices. In accordance with Section 7(b) of the GNU General Public 
#License version 3, these Appropriate Legal Notices must retain the display of 
#the "Powered by cyn.in" AND "A Cynapse Invention" logos. You should have 
#received a copy of the detailed Additional Terms License with this program.
#
#This program is distributed in the hope that it will be useful,
#but WITHOUT ANY WARRANTY; without even the implied warranty of 
#MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General 
#Public License for more details.
#
#You should have received a copy of the GNU General Public License along with 
#this program.  If not, see <http://www.gnu.org/licenses/>.
#
#You can contact Cynapse at support@cynapse.com with any problems with cyn.in. 
#For any queries regarding the licensing, please send your mails to 
# legal@cynapse.com
#
#You can also contact Cynapse at:
#802, Building No. 1,
#Dheeraj Sagar, Malad(W)
#Mumbai-400064, India
###############################################################################
from zope.interface import implements
from zope.component import adapts

from borg.localrole.interfaces import ILocalRoleProvider
from ubify.spaces.interfaces import ISpace
from StringIO import StringIO
from logging import getLogger
from Products.CMFCore.utils import getToolByName

from Products.CMFCore.WorkflowCore import WorkflowException

class LocalRoles(object):
    """Provide a local role manager for Spaces
    """
    implements(ILocalRoleProvider)
    adapts(ISpace)

    def __init__(self, context):
        self.context = context
#        self.req = context.REQUEST
#        self.reqpath = self.req.environ['PATH_TRANSLATED']
#        self.actobj = context.unrestrictedTraverse(self.reqpath)
#        wft = getToolByName(context, 'portal_workflow')
#        try:
#            self.currstate = wft.getInfoFor(self.actobj,"review_state")
#        except WorkflowException:
#            self.currstate = "unknown"
#            pass
#        getLogger().info("localroles init, context = %s, actobj = %s, actobj_state = %s " % (context,self.actobj,self.currstate))

    def getAllRoles(self):
        #import pdb;pdb.set_trace()
        for m in self.context.managers:
            yield (m, 'Manager',)        
        for m in self.context.members:
            yield (m, 'TeamMember',)            
        for m in self.context.groups:
            yield (m, 'TeamMember',)
        for m in self.context.viewers:
            yield (m,'SpaceViewer',)
        for m in self.context.viewergroups:
            yield (m,'SpaceViewer',)
        for m in self.context.creators:
            yield (m,'Owner',)

    def getRoles(self, principal_id):
#        import pdb; pdb.set_trace()
        roles = set()
        if principal_id in self.context.managers:
            roles.add('Manager')
        if principal_id in self.context.members:
            roles.add('TeamMember')            
        if principal_id in self.context.groups:            
            roles.add('TeamMember')            
        if principal_id in self.context.viewers:
            roles.add('SpaceViewer')
        if principal_id in self.context.viewergroups:
            roles.add('SpaceViewer')
        if principal_id in self.context.creators:
            roles.add('Owner')
        if principal_id in self.context.viewers:
            roles.add('SpaceViewer')
        if principal_id in self.context.viewergroups:
            roles.add('SpaceViewer')
 #       getLogger().info("getRoles, principal_id = %s, context = %s, Roles= %s" % (principal_id,self.context, [role for role in roles]))
        
        return roles
