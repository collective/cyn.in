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
from Products.Five import BrowserView
from Products.CMFCore.utils import getToolByName
from AccessControl import getSecurityManager
from Acquisition import aq_inner, aq_parent
from zope.interface import implements
from interfaces import IAdminFunctions
from xmlrpclib import Fault
import logging

class AdminFunctions(BrowserView):
    """Implements function that are only callable by people who have the cmf.ManagePortal or Manage portal
    permission"""
    implements(IAdminFunctions)

    def canAdmin(self):
        """Returns "yes" if the calling user has the cmf.ManagePortal permission else Faults
            the XMLRPC call"""
        return "yes"
    
    def registerUser(self,username,email,fullname,notifyUser=False,password=None):
        """Create a user with passed parameters.
            username and email are required minimally.
            If password is not passed then one is generated.
            If notifyUser is set to true then the user will be emailed a link to allow them to set their own password.
            return True if succeeded, else Fault
        """
        LOG = logging.getLogger('ubify.xmlrpc')
        properties = {
            'username' : username,
            'fullname' : fullname,
            'email' : email.strip(),
        }
        #try:
        regtool = getToolByName(self, 'portal_registration')
        pwtool = getToolByName(self, 'portal_password_reset')
        if password == None:
            password = regtool.generatePassword()
        
        regtool.addMember(username,password, properties=properties)
        if notifyUser:
            regtool.registeredNotify(username)
        resetdata = pwtool.requestReset(username)
        LOG.info("Created user: user: %s, email: %s, fullname: %s" % (username,email,fullname))
        return resetdata
        #except ValueError, e:
        #    raise Fault(501,e.__str__())
        #    #raise ValueError, e.__str__()

    def verifyUser(self,username,code):
        """Checks that the verification code provided is correct for allowing (in a separate call) reset of password"""
        LOG = logging.getLogger('ubify.xmlrpc')
        pwtool = getToolByName(self, 'portal_password_reset')
        pwtool.verifyKey(code)
        LOG.info("Randomstring verified for user: %s" % username)
        return True
    def setPasswordByReset(self,username,password,randomstring):
        """
            Sets a user's password. Does NOT notify the user of this change. Use resetPassword if you want the user to get an email on password change.
        """
        LOG = logging.getLogger('ubify.xmlrpc')
        pwtool = getToolByName(self, 'portal_password_reset')
        pwtool.resetPassword(username, randomstring, password)
        LOG.info("User set their password after reset: %s" % username)
        return True

    def resetPassword(self,username):
        """
            Resets a user's password, and emails the user a link to allow them to come and change their password.
        """
        pass

    def addUserToGroup(self,username,groups=[]):
        """Adds user with passed username to groups specified in groups parameter.
            If groups are not present, they are first created and then the user is assigned to them.
        """
        pass

    def removeUserFromGroup(self,username,groups=[]):
        """Removes user with passed username from groups specified in groups parameter.
            If any of the passed groups do not exist, they are skipped silently.
        """
        pass

    def editUserProfile(self,username,keyvaluedict):
        """Updates user properties with passed values in key value dict.
            If any of the passed property names do not exist they are skipped silently.
            If the keyvaluedict contains a term with name 'password' the user's password will be set to the value of this term.
            If the keyvaluedict contains a term with name 'avatar' the user's avatar will be set from the url of the value of this term.
        """
        pass
    
    def setUserAvatar(self,username,avatarURL):
        """Set's the users avatar by downloading the image from avatarURL"""
        pass
    
    def addGroup(self,groupname):
        """Add's the groupname specified. Does not throw an error if the group already exists."""
        pass
    
    def removeGroup(self,groupname):
        """Remove's the groupname specified. Returns True if successful or False if the groupname does not exist"""
        pass
    
    def deleteItemByUID(self,UID):
        """Delete's an item which has the passed UID. Throws fault if UID does not exist."""
        pass
    
    def userExistsByEmail(self,email):
        """Returns true if a user with that email exists, false if not"""
        acl = self.context.acl_users
        for user in acl.getUsers():
            if user.getProperty('email') == email:
                return True
            
        return False
    
