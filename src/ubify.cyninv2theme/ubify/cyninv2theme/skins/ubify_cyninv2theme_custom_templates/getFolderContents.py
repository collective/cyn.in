###############################################################################
##cyn.in is an open source Collaborative Knowledge Management Appliance that 
##enables teams to seamlessly work together on files, documents and content in 
##a secure central environment.
##
##cyn.in v2 an open source appliance is distributed under the GPL v3 license 
##along with commercial support options.
##
##cyn.in is a Cynapse Invention.
##
##Copyright (C) 2008 Cynapse India Pvt. Ltd.
##
##This program is free software: you can redistribute it and/or modify it under
##the terms of the GNU General Public License as published by the Free Software 
##Foundation, either version 3 of the License, or any later version and observe 
##the Additional Terms applicable to this program and must display appropriate 
##legal notices. In accordance with Section 7(b) of the GNU General Public 
##License version 3, these Appropriate Legal Notices must retain the display of 
##the "Powered by cyn.in" AND "A Cynapse Invention" logos. You should have 
##received a copy of the detailed Additional Terms License with this program.
##
##This program is distributed in the hope that it will be useful,
##but WITHOUT ANY WARRANTY; without even the implied warranty of 
##MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General 
##Public License for more details.
##
##You should have received a copy of the GNU General Public License along with 
##this program.  If not, see <http://www.gnu.org/licenses/>.
##
##You can contact Cynapse at support@cynapse.com with any problems with cyn.in. 
##For any queries regarding the licensing, please send your mails to 
## legal@cynapse.com
##
##You can also contact Cynapse at:
##802, Building No. 1,
##Dheeraj Sagar, Malad(W)
##Mumbai-400064, India
###############################################################################
## Script (Python) "getFolderContents"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=contentFilter=None,batch=False,b_size=100,full_objects=False,sort_on=None,sort_order=None
##title=wrapper method around to use catalog to get folder contents
##

mtool = context.portal_membership
cur_path = '/'.join(context.getPhysicalPath())
path = {}

if not contentFilter:
    # The form and other are what really matters
    contentFilter = dict(getattr(context.REQUEST, 'form',{}))
    contentFilter.update(dict(getattr(context.REQUEST, 'other',{})))
else:
    contentFilter = dict(contentFilter)

if not contentFilter.get('sort_on', None):
    contentFilter['sort_on'] = 'getObjPositionInParent'

if contentFilter.get('path', None) is None:
    path['query'] = cur_path
    path['depth'] = 1
    contentFilter['path'] = path

if sort_on <> None:
    contentFilter['sort_on'] = sort_on
    
if sort_order <> None:
    contentFilter['sort_order'] = sort_order



show_inactive = mtool.checkPermission('Access inactive portal content', context)

# Evaluate in catalog context because some containers override queryCatalog
# with their own unrelated method (Topics)
contents = context.portal_catalog.queryCatalog(contentFilter, show_all=1,
                                                  show_inactive=show_inactive)

if full_objects:
    contents = [b.getObject() for b in contents]

if batch:
    from Products.CMFPlone import Batch
    b_start = context.REQUEST.get('b_start', 0)
    batch = Batch(contents, b_size, int(b_start), orphan=0)
    return batch

return contents
