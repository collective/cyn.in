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
from StringIO import StringIO
from Products.CMFCore.utils import getToolByName
from Products.PlonePAS.Extensions.Install import activatePluginInterfaces

#from borg.localrole.utils import setup_localrole_plugin
from ubify.spaces.config import PLACEFUL_WORKFLOW_POLICY
from ubify.spaces.config import SPACE_PLACEFUL_WORKFLOW_POLICY
from ubify.spaces.config import spacecontentworkflowtypes,applicationworkflowtypes
from ubify.spaces.config import REVIEW_PLACEFUL_WORKFLOW_POLICY
from ubify.spaces.config import APPLICATION_PLACEFUL_WORKFLOW_POLICY


def add_placeful_workflow_policy(portal):
    """Add the placeful workflow policy used by Spaces.
    """
    out = StringIO()
    
    placeful_workflow = getToolByName(portal, 'portal_placeful_workflow', None)
    
    if placeful_workflow is None:
        print >> out, "Cannot install placeful workflow policy - CMFPlacefulWorkflow not available"
    elif SPACE_PLACEFUL_WORKFLOW_POLICY not in placeful_workflow.objectIds():
        placeful_workflow.manage_addWorkflowPolicy(SPACE_PLACEFUL_WORKFLOW_POLICY, 
                                                   duplicate_id='portal_workflow')
        policy = placeful_workflow.getWorkflowPolicyById(SPACE_PLACEFUL_WORKFLOW_POLICY)
        policy.setTitle('Space workflow')
        policy.setDefaultChain((SPACE_PLACEFUL_WORKFLOW_POLICY,))
        policy.setChainForPortalTypes(('Space','ContentSpace',), SPACE_PLACEFUL_WORKFLOW_POLICY)
        print >> out, "Installed workflow policy %s" % SPACE_PLACEFUL_WORKFLOW_POLICY
    else:
        policy = placeful_workflow.getWorkflowPolicyById(SPACE_PLACEFUL_WORKFLOW_POLICY)
        if policy <> None:
            for et in ('Space',):                
                if policy._chains_by_type.get(et) is None:
                    portal_types = getattr(portal,'portal_types')
                    obj = getattr(portal_types,et)
                    if obj <> None:                        
                        tid = obj.getId()
                        policy.setChain(tid,'(Default)')
            policy.setChainForPortalTypes(('Space',), SPACE_PLACEFUL_WORKFLOW_POLICY)
            try:
                ptypes = portal.portal_types
                hascontentspace = getattr(ptypes,'ContentSpace')
                if hascontentspace:
                    policy.setChainForPortalTypes(('Space','ContentSpace',), SPACE_PLACEFUL_WORKFLOW_POLICY)
            except AttributeError:
                pass
        print >> out, "Workflow policy %s already installed" % SPACE_PLACEFUL_WORKFLOW_POLICY
    
    
    if placeful_workflow is None:
        print >> out, "Cannot install placeful workflow policy - CMFPlacefulWorkflow not available"
    elif PLACEFUL_WORKFLOW_POLICY not in placeful_workflow.objectIds():
        placeful_workflow.manage_addWorkflowPolicy(PLACEFUL_WORKFLOW_POLICY, 
                                                   duplicate_id='portal_workflow')
        policy = placeful_workflow.getWorkflowPolicyById(PLACEFUL_WORKFLOW_POLICY)
        policy.setTitle('Space content workflow')
        policy.setDefaultChain((PLACEFUL_WORKFLOW_POLICY,))
        policy.setChainForPortalTypes((spacecontentworkflowtypes), PLACEFUL_WORKFLOW_POLICY)
        try:
            policy.setChainForPortalTypes((applicationworkflowtypes), APPLICATION_PLACEFUL_WORKFLOW_POLICY)
        except:
            print >> out, "Exception"
        try:
            policy.setChainForPortalTypes(('ContentSpace',), SPACE_PLACEFUL_WORKFLOW_POLICY)
        except:
            print >> out, "Exception"
        print >> out, "Installed workflow policy %s" % PLACEFUL_WORKFLOW_POLICY
    else:
        policy = placeful_workflow.getWorkflowPolicyById(PLACEFUL_WORKFLOW_POLICY)
        if policy <> None:
            for et in spacecontentworkflowtypes:
                if policy._chains_by_type.get(et) is None:
                    portal_types = getattr(portal,'portal_types')
                    obj = getattr(portal_types,et)
                    if obj <> None:                        
                        tid = obj.getId()
                        policy.setChain(tid,'(Default)')
            policy.setChainForPortalTypes((spacecontentworkflowtypes), PLACEFUL_WORKFLOW_POLICY)
            try:
                policy.setChainForPortalTypes((applicationworkflowtypes), APPLICATION_PLACEFUL_WORKFLOW_POLICY)
            except:
                print >> out, "Exception"
            try:
                policy.setChainForPortalTypes(('ContentSpace',), SPACE_PLACEFUL_WORKFLOW_POLICY)
            except:
                print >> out, "Exception"
        print >> out, "Workflow policy %s already installed" % PLACEFUL_WORKFLOW_POLICY

        
    if placeful_workflow is None:
        print >> out, "Cannot install placeful workflow policy - CMFPlacefulWorkflow not available"
    elif REVIEW_PLACEFUL_WORKFLOW_POLICY not in placeful_workflow.objectIds():
        placeful_workflow.manage_addWorkflowPolicy(REVIEW_PLACEFUL_WORKFLOW_POLICY, 
                                                   duplicate_id='portal_workflow')
        policy = placeful_workflow.getWorkflowPolicyById(REVIEW_PLACEFUL_WORKFLOW_POLICY)
        policy.setTitle('Space review content workflow')
        policy.setDefaultChain((REVIEW_PLACEFUL_WORKFLOW_POLICY,))
        policy.setChainForPortalTypes((spacecontentworkflowtypes), REVIEW_PLACEFUL_WORKFLOW_POLICY)
        try:
            policy.setChainForPortalTypes((applicationworkflowtypes), APPLICATION_PLACEFUL_WORKFLOW_POLICY)
        except:
            print >> out, "Exception"
        try:
            policy.setChainForPortalTypes(('ContentSpace',), SPACE_PLACEFUL_WORKFLOW_POLICY)
        except:
            print >> out, "Exception"
        print >> out, "Installed workflow policy %s" % REVIEW_PLACEFUL_WORKFLOW_POLICY
    else:
        policy = placeful_workflow.getWorkflowPolicyById(REVIEW_PLACEFUL_WORKFLOW_POLICY)
        if policy <> None:
            for et in spacecontentworkflowtypes:
                if policy._chains_by_type.get(et) is None:
                    portal_types = getattr(portal,'portal_types')
                    obj = getattr(portal_types,et)
                    if obj <> None:                        
                        tid = obj.getId()
                        policy.setChain(tid,'(Default)')
            policy.setChainForPortalTypes((spacecontentworkflowtypes), REVIEW_PLACEFUL_WORKFLOW_POLICY)
            try:
                policy.setChainForPortalTypes((applicationworkflowtypes), APPLICATION_PLACEFUL_WORKFLOW_POLICY)
            except:
                print >> out, "Exception"
            try:
                policy.setChainForPortalTypes(('ContentSpace',), SPACE_PLACEFUL_WORKFLOW_POLICY)
            except:
                print >> out, "Exception"
        print >> out, "Workflow policy %s already installed" % REVIEW_PLACEFUL_WORKFLOW_POLICY
        
    return out.getvalue()

def migration(portal):
    ct = getattr(portal,'portal_catalog')
    spaces = [s.getObject() for s in ct(portal_type='Space')]
    for o in spaces:
        fti = o.getTypeInfo()
        try:
            if getattr(fti,'view_methods'):
                fti._updateProperty('view_methods',('view',))
        except:
            pass
    
def importVarious(context):
    """
    Import various settings.

    Provisional handler that does initialization that is not yet taken
    care of by other handlers.
    """
    out = StringIO()
    if context.readDataFile('ubify_spaces_various.txt') is None:
        return
    site = context.getSite()
    
#    print >> out, setup_localrole_plugin(site)
    print >> out, add_placeful_workflow_policy(site)
    print >> out, migration(site)
    
    logger = context.getLogger("ubify.spaces")
    logger.info(out.getvalue())