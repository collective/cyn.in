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
from zope.i18nmessageid import MessageFactory
from Products.CMFCore.permissions import setDefaultRoles
from AccessControl import allow_module
from AccessControl import ModuleSecurityInfo
from Products.AdvancedQuery import Eq, Between, Le


setDefaultRoles("SmartView Add Smart view", ('Manager'))

def initialize(context):
    """Initializer called when used as a Zope 2 product."""
    ModuleSecurityInfo("ubify.smartview").declarePublic("getResults")
    ModuleSecurityInfo("ubify.smartview").declarePublic("getQValue")
    ModuleSecurityInfo("ubify.smartview").declarePublic("getProcessResultForTimeLineView")
    
    pass

def getResults(context):
    results = []
    try:
        results = context.portal_catalog.searchResults(getQValue(context))
    except (RuntimeError,TypeError,NameError):
        pass
    return results

def getQValue(context):
    result = ""
    enquery = context.query.encode().lstrip(" ")
    enquery = enquery.rstrip(" ")
    if enquery <> "":
        result = eval(enquery)
    return result

def getProcessResultForTimeLineView(results):
    months = []
    month_info = []
    old_month_year = None
    #import pdb;pdb.set_trace()
    for obj in results:        
        month = str(obj.modified().month())
        year = str(obj.modified().year())
        month_year = year + month
        if month_year != old_month_year:
            old_month_year = month_year
            if month_info:
                months.append(month_info)
            month_info = {'month': obj.modified().month(),
                          'year': obj.modified().year(),
                          'month_name': obj.modified().strftime("%B"),
                          'objects': []}
        event_dict = {'object': obj,
                    'day': obj.modified().day(),
                    'start': obj.modified(),
                    'created': obj.created(),
                    'location': '',
                    'title': obj.title,
                    'description': obj.description,
                    'url': obj.absolute_url(),
                    }
        month_info['objects'].append(event_dict)

    if month_info:
        months.append(month_info)
        
    results = months
    return results