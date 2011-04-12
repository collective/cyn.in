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
========================================================
 ubify.spaces : Collaborative workspaces for the masses
========================================================
    
    Originally by Martin Aspeli <optilude@gmx.net>
    Adapted for usage as Spaces for Cynapse Ubify by Dhiraj Gupta <dhiraj@cynapse.com>

This product is based on b-org, and only runs on Plone 3. It depends on
the borg.localrole package.

Place these packages in your PYTHONPATH or install them into a buildout or
a workingenv, and then use Plone's Add-on product configuration to install.

With borg.project, you can create a folder in the portal with:

 - a number of users assigned as managers, given a local Manager role
 
 - a number of users assigned as team members, given a local TeamMember role
 
 - a custom workflow, as specified by a CMFPlacefulWorkflow policy
 
 - an explicitly managed list of addable content types
 
The default version of the project workflow contains states for content
being published, visible only to team members, or completely private.

Setting up a new project
------------------------

First, we need to add a few members

    >>> from Products.CMFCore.utils import getToolByName
    >>> membership = getToolByName(self.portal, 'portal_membership')
    
    >>> membership.addMember('member1', 'secret', ('Member',), ())
    >>> membership.addMember('member2', 'secret', ('Member',), ())
    >>> membership.addMember('member3', 'secret', ('Member',), ())
    >>> membership.addMember('member4', 'secret', ('Member',), ())
    >>> membership.addMember('member5', 'secret', ('Member',), ())

and a group, with a single member

    >>> groups = getToolByName(self.portal, 'portal_groups')
    >>> _ = groups.addGroup('group1')
    >>> _ = groups.addPrincipalToGroup('member4', 'group1')

We need to be the a manager to create the project workspace.

    >>> self.loginAsPortalOwner()
    
We can now create the project object. Will simulate what happens in the
add form here, by setting the relevant properties on a newly created object,
calling _finishConstruction() on its FTI to finalise workflow creation, and
send the IObjectCreatedEvent event.

Notice how managers and members are lists of user ids.

    >>> from zope.component import createObject
    >>> project1 = createObject(u"borg.project.Project")

    >>> project1.id = 'project1'
    >>> project1.title = "Project 1"
    >>> project1.description = "A first project"
    >>> project1.managers = ('member1', 'member2',)
    >>> project1.members = ('member2', 'member3',)
    >>> project1.groups = ('group1',)

Workflow policies are obtained from a vocabulary. The default vocabulary
simply returns a particular policy which is installed at setup time.

    >>> from zope.schema.interfaces import IVocabularyFactory
    >>> from zope.component import getUtility
    >>> policies_factory = getUtility(IVocabularyFactory, name=u"borg.project.WorkflowPolicies")
    >>> policies_vocabulary = policies_factory(self.portal)
    >>> workflow_policy = list(policies_vocabulary)[0]
    >>> workflow_policy.value
    'borg_project_placeful_workflow'

    >>> project1.workflow_policy = workflow_policy.value

Addable types are from another vocabulary, which should include any
globally allowed types.

    >>> types_factory = getUtility(IVocabularyFactory, name=u"borg.project.AddableTypes")
    >>> types_vocabulary = types_factory(self.portal)
    >>> 'Document' in [v.value for v in types_vocabulary]
    True
    >>> 'Topic' in [v.value for v in types_vocabulary]
    True
    
There is also a method to get default values for the addable types field.
This gives back all globally allowed types with Owner in the list of roles
for their add permissions.

    >>> from borg.project.utils import default_addable_types
    >>> default_addable = default_addable_types(self.portal)
    >>> 'Document' in default_addable
    True
    >>> 'Topic' in default_addable
    False
    
    >>> project1.addable_types = ('Document', 'Folder',)

Now let us finish construction and fire those events.

    >>> from zope.event import notify
    >>> from zope.lifecycleevent import ObjectCreatedEvent
    >>> notify(ObjectCreatedEvent(project1))

    >>> new_id = self.portal._setObject('project1', project1)
    >>> project1 = self.portal._getOb(new_id)
    >>> _ = project1.getTypeInfo()._finishConstruction(project1)

With this, the project is properly constructed. Let us verify that the
local policy is in place.

    >>> placeful_workflow = getToolByName(self.portal, 'portal_placeful_workflow')
    >>> placeful_workflow.getWorkflowPolicyConfig(project1).getPolicyBelowId()
    'borg_project_placeful_workflow'
    
And that our members have the appropriate roles

    >>> acl_users = getToolByName(self.portal, 'acl_users')

This user is a manager only.

    >>> member1 = acl_users.getUserById('member1')
    >>> 'Manager' in member1.getRolesInContext(project1)
    True
    >>> 'TeamMember' in member1.getRolesInContext(project1)
    False
    
This user is a manager and a member.
    
    >>> member2 = acl_users.getUserById('member2')
    >>> 'Manager' in member2.getRolesInContext(project1)
    True
    >>> 'TeamMember' in member2.getRolesInContext(project1)
    True
    
This user is a member only.
    
    >>> member3 = acl_users.getUserById('member3')
    >>> 'Manager' in member3.getRolesInContext(project1)
    False
    >>> 'TeamMember' in member3.getRolesInContext(project1)
    True

This user is associated by way of the group.

    >>> member4 = acl_users.getUserById('member4')
    >>> 'Manager' in member4.getRolesInContext(project1)
    False
    >>> 'TeamMember' in member4.getRolesInContext(project1)
    True

This user has no association with the group.

    >>> member5 = acl_users.getUserById('member5')
    >>> 'Manager' in member5.getRolesInContext(project1)
    False
    >>> 'TeamMember' in member5.getRolesInContext(project1)
    False
    
Finally, let us verify that the permission management has worked. The key
here is that users with the TeamMember role should be able to add the types
we explicitly defined, but no other types.

The two managers can add other content, though.

    >>> self.login('member1')
    >>> project1.invokeFactory('Document', 'd1')
    'd1'
    >>> project1.invokeFactory('Image', 'i1')
    'i1'

    >>> self.login('member2')
    >>> project1.invokeFactory('Document', 'd2')
    'd2'
    >>> project1.invokeFactory('Image', 'i2')
    'i2'
    
    >>> self.login('member3')
    >>> project1.invokeFactory('Document', 'd3')
    'd3'
    >>> project1.invokeFactory('Image', 'i3')
    Traceback (most recent call last):
    ...
    Unauthorized: Cannot create Image    

    >>> self.login('member4')
    >>> project1.invokeFactory('Document', 'd4')
    'd4'
    >>> project1.invokeFactory('Image', 'i4')
    Traceback (most recent call last):
    ...
    Unauthorized: Cannot create Image
    
But of course, a user who is not a team member can't add anything.

    >>> self.login('member5')
    >>> project1.invokeFactory('Document', 'd5')
    Traceback (most recent call last):
    ...
    Unauthorized: Cannot create Document
    >>> project1.invokeFactory('Image', 'i5')
    Traceback (most recent call last):
    ...
    Unauthorized: Cannot create Image