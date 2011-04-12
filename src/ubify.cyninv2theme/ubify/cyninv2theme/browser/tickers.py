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
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.CMFCore.utils import getToolByName
from DateTime import DateTime
from urllib import urlopen
from zope.app.component.hooks import getSite
from Products.Five.browser import BrowserView
from ubify.cyninv2theme import CyninEdition

def versioncheck(updateroot,versionstring):
    returnval = False
    if updateroot is not None:
        ce = updateroot.find('communityedition')
        if ce is not None:
            current = ce.find('current')
            if current is not None:
                versionmajor = current.find('versionmajor').text
                versionminor = current.find('versionminor').text
                versiondisposition = current.find('versiondisposition').text
                
                ubifyversion = versionstring
                cur_disposition = ""
                cur_major = ""
                cur_minor = ""
                
                if versionstring.endswith('dev'):
                    cur_disposition = 'dev'
                    ubifyversion = ubifyversion.rstrip('dev')
                    
                arr_version = ubifyversion.split('.')
                
                if len(arr_version) > 0:
                    cur_major = arr_version[0]
                    
                if len(arr_version) > 1:
                    cur_minor = arr_version[1]
                    
                try:
                    iv_major = int(versionmajor)
                    iv_minor = int(versionminor)
                    
                    ic_major = int(cur_major)
                    ic_minor = int(cur_minor)
                    
                    #first check for major
                    if iv_major > ic_major:
                        returnval = True                        
                    elif iv_major == ic_major:                            
                        #then check for minor
                        if iv_minor > ic_minor:
                            returnval = True
                        elif iv_minor == ic_minor:
                            #then check for disposition currently do nothing
                            returnval = False
                        else:
                            returnval = False
                    else:
                        returnval = False
                except:
                    pass
    return returnval 
        
def updateversion():
    thesite = getSite()
    portal_quickinstaller = getToolByName(thesite, 'portal_quickinstaller')
    versionstring = ''
    try:
        objProduct = portal_quickinstaller._getOb('ubify.policy')
    except:
        return
    if objProduct <> None:
        versionstring = objProduct.getInstalledVersion()

    ##########Version Check ##################
    portal_properties = getToolByName(thesite, 'portal_properties')
    is_update_check_enabled = portal_properties.site_properties.enable_update_check
    update_check_url = portal_properties.site_properties.update_check_url
    newversionavailable = False

    if is_update_check_enabled:
        site = thesite.portal_url.getPortalObject()
        if not site.hasProperty('siteuid'):
            from Products.Archetypes.utils import make_uuid
            newuid = make_uuid()
            site.manage_addProperty('siteuid',newuid,'string')
            siteuid = newuid
        else:
            siteuid = site.getProperty('siteuid')
        if site.hasProperty('lastupdatecheck'):
            slastcheck = site.getProperty('lastupdatecheck')
            lastcheck = DateTime(slastcheck)
        else:
            lastcheck = DateTime() - 30  # Since last update check date time was not found, let's make it 30 days earlier

        if lastcheck < DateTime() - 1: #If it's been more than 1 day since last check
            print 'Last update check was at %s, shouldcheck = %s, now-1=%s' % (lastcheck, (lastcheck < DateTime() - 1),DateTime() -1)
            from lxml import etree
            import socket
            timeout = 10 # timeout in seconds
            socket.setdefaulttimeout(timeout)
            editionname,editioncode = CyninEdition(thesite)
            updateroot = None
            #try:
            updateroot = etree.parse(update_check_url % (versionstring,siteuid,editioncode))
            #except:
            #    updateroot = None
            if updateroot is not None:
                lastcheck=DateTime() #Update the lastcheck date time to now.
                ce = updateroot.find('communityedition')
                if ce is not None:
                    current = ce.find('current')
                    if current is not None:
                        ver = current.find('versionstring')
                        if ver is not None:
                            verstring = ver.text
                            if versioncheck(updateroot,versionstring):
                                #We have a new version!!
                                newversionavailable = True
                                newversionstring = verstring
                                changelog = current.find('changelogurl')
                                if changelog is not None:
                                    changelogurl = changelog.text
                                download = current.find('downloadurl')
                                if download is not None:
                                    downloadurl = download.text
                                if site.hasProperty('lastupdatecheck'):
                                    site._updateProperty('lastupdatecheck',lastcheck)
                                else:
                                    site.manage_addProperty('lastupdatecheck',lastcheck,'string')
                            else:
                                if site.hasProperty('lastupdatecheck'):
                                    site._updateProperty('lastupdatecheck',lastcheck)
                                else:
                                    site.manage_addProperty('lastupdatecheck',lastcheck,'string')
                                if site.hasProperty('newversionstring'):
                                    site._delProperty('newversionstring')
                                if site.hasProperty('changelogurl'):
                                    site._delProperty('changelogurl')
                                if site.hasProperty('downloadurl'):
                                    site._delProperty('downloadurl')
                        else:
                            print 'version node not found'
                    else:
                        print 'current node not found'
                else:
                    print 'CE node not found'
            else:
                print 'Empty parse, updateroot is None!'
        if newversionavailable: #The update check figured out a new version so let's cache it.
            if site.hasProperty('newversionstring'):
                site._updateProperty('newversionstring',newversionstring)
            else:
                site.manage_addProperty('newversionstring',newversionstring,'string')
            if site.hasProperty('changelogurl'):
                site._updateProperty('changelogurl',changelogurl)
            else:
                site.manage_addProperty('changelogurl',changelogurl,'string')
            if site.hasProperty('downloadurl'):
                site._updateProperty('downloadurl',downloadurl)
            else:
                site.manage_addProperty('downloadurl',downloadurl,'string')
        else:
            ## Finally check if we have saved newversion data in properties and use it.
            if site.hasProperty('newversionstring'):
                newversionavailable = True
                newversionstring = site.getProperty('newversionstring')
                changelogurl = site.getProperty('changelogurl')
                downloadurl = site.getProperty('downloadurl')

    ##########End Version Check ################

class TickTriggerView(BrowserView):
    """ View that is called by Zope clock server.
    
    """
    def __call__(self):
        updateversion()
        return "OK"
