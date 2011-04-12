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
## Script (Python) "queryfolderbytype"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=REQUEST=None,show_all=0,quote_logic=0,quote_logic_indexes=['SearchableText','Description','Title'],use_types_blacklist=False,show_inactive=False,use_navigation_root=False,contentFilter=None,batch=False,b_size=100,full_objects=False,is_month_view=False,depth=-1,sorton='modified',sortorder='descending',currentpath=None,types_to_search=('Document','Event','Blog Entry','File','Image','Link','StatuslogItem','Video','Discussion','Audio'),creator=None,modifiers=None
##title=wraps the portal_catalog with a rules qualified query
##
from ubify.cyninv2theme import getAllItemsForContext, getTagsAndTagsCount
from DateTime import DateTime

results=[]

resultimages = {}
path = {}
mtool = context.portal_membership
cur_path = '/'.join(context.getPhysicalPath())

if currentpath is None:
    currentpath = cur_path
    
if not contentFilter:
    # The form and other are what really matters
    contentFilter = dict(getattr(context.REQUEST, 'form',{}))
    contentFilter.update(dict(getattr(context.REQUEST, 'other',{})))
else:
    contentFilter = dict(contentFilter)
    
if not contentFilter.get('sort_on', None):
    contentFilter['sort_on'] = sorton
    
if not contentFilter.get('sort_order',None):
    contentFilter['sort_order'] = sortorder

if contentFilter.get('path', None) is None:
    path['query'] = currentpath
    if depth > 0:
        path['depth'] = depth    
    contentFilter['path'] = path
    
if contentFilter.get('portal_type', None) is None and types_to_search <> None:
    contentFilter['portal_type'] = types_to_search

#sumant: code for date range filter starts here
cstartdate = contentFilter.get('startdate',None)
cenddate = contentFilter.get('enddate',None)

cdateparam = contentFilter.get('sort_on')
if cdateparam in ('sortable_title',):
    cdateparam = sorton

csdateparam = ''
cedateparam = ''

customdatequery = {'query':(),'range':''}

if cstartdate is not None and cstartdate is not '':
    csdateparam = contentFilter['startdate']

if cenddate is not None and cenddate is not '':
    cedateparam = contentFilter['enddate']

if csdateparam != '' and cedateparam != '':
    customdatequery['query'] = (DateTime(csdateparam),DateTime(cedateparam))
    customdatequery['range'] = 'min:max'    
elif csdateparam != '':
    customdatequery['query'] = (DateTime(csdateparam),)
    customdatequery['range'] = 'min'
elif cedateparam != '':
    customdatequery['query'] = (DateTime(cedateparam))
    customdatequery['range'] = 'max'
    
if csdateparam != '' or cedateparam != '':
    contentFilter[cdateparam] = customdatequery

#sumant: code for date range filter ends here

if contentFilter.get('Creator', None) is None and modifiers <> None:
    contentFilter['modifiers'] = {'operator': 'or', 'query': modifiers}

show_inactive = mtool.checkPermission('Access inactive portal content', context)

#results = getAllItemsForContext(context,currentpath,types_to_search,depth,sorton,sortorder,creator,modifiers)
results = context.portal_catalog.queryCatalog(contentFilter, show_all=1,show_inactive=show_inactive)

tagslist = getTagsAndTagsCount(results)

itemcount = len(results)

if full_objects:
    results = [b.getObject() for b in results]

if batch:
    from Products.CMFPlone import Batch
    b_start = context.REQUEST.get('b_start', 0)
    batch = Batch(results, b_size, int(b_start), orphan=0)
    return batch, tagslist, itemcount

if types_to_search == ('Image',):
    resultimages['images'] = results
    return resultimages, tagslist, itemcount

return results,tagslist,itemcount
