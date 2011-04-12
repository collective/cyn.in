from zope.component import Interface, adapts
from zope.interface import implements

class IXMLRPCFolder(Interface):
    """Provides xmlrpc methods on a folderish object"""
    def ListFolderContents():
        """ Returns a list of objectIds"""

class IStackerAPI(Interface):
    """Interface to the StackerAPI
    """
    def sayhello():
        """Returns a string with Hello
        """
    def echo(self,echostr):
        """Returns the passed string"""
    def getSiteTitle(self):
        """Return the site title"""
    def getSiteInfo(self):
        """Return site relevant information in a struct/dic"""
    def getRecentUpdates(self,maxitemcount=5,pagenumber=1):
        """Return the recent updates"""
    def refreshUpdateItem(self,uid):
        """Resends a single item of the same structure as the one in getRecentUpdates with the most updated info"""
    def getTypeInfo(self,typename):
        """Returns the type title and icon url for given typename"""
    def getUserInfo(self,userid):
        """Return the user name details, and avatar url for given userid"""
    def getWikiBody(self,uid):
        """Return the wiki body text, pre-cooked and processed"""
    def getEventInfo(self,uid):
        """Return the information available for a Calendar Event"""
    def getFileInfo(self,uid):
        """Return the info available for a file"""
    def getLinkInfo(self,uid):
        """Return the info available for a link"""
    def getBlogEntry(self,uid):
        """Return the info available for a Blog Entry"""
    def getComments(self,uid):
        """Return all the comments for the given object's UID"""
    def getCommentsRecursive(self,uid):
        """Return all the comments for the given object's UID. The returned comments are arranged recursively in a children object"""
    def addNewComment(self,uid,subject,text,commenter):
        """Adds a comment on the provided UID with given subject, text and commenter user"""
    ###Method does not exist
    ###def replyToComment(self,uid,subject,text,commenter):
    ###    """Replies to the given comment's UID with given subject, text and commenter user"""    
    def getUpdateCount(self):
        """Returns number of recent items available for recent user"""
    def search(self,searchableText,maxitemcount=5,pagenumber=1):
        """Returns result for search text entered for recent user"""
    def searchIds(self,searchableText='',maxitemcount=5,pagenumber=1):
        """Returns search results with only id, lastchangedate and relevance for search text entered."""
    def getStatusMessages(self,username='',count=1,pagenumber=1):
        """Returns current status message for passed username. For empty username method returns status message for current user"""
    def getStatusMessage(self,username=''):
        """Returns current status message of passed user as string"""
    def setStatusMessage(self,message):
        """Set status log message for current user"""
    def getLastChangeDate(self):
        """Returns the max lastchangedate for the logged in user."""
    def getRecentItemIds(self,maxitemcount=5,pagenumber=1):
        """Return the recent UIDs, up to a maximum of maxitemcount items will be returned in a list"""
    def getSearchItemsByIds(self,arrUIDs):
        """Return the search items as per the UIDs requested."""
    def getItemsByIds(self,maxitemcount=5,pagenumber=1):
        """Return the Update items as per the UIDs requested."""
    def getUsersByIds(self,arrUserIds):
        """Return the user info objects for the users specified"""
    def getTypesByNames(self,arrTypeNames):
        """Return the type info objects for the type names specified"""
    def getItemsSinceDate(self,fromDate):
        """Returns items count and items changed after passed date.Date should be in milliseconds."""
    def getItemsCountSinceDate(self,fromDate):
        """Returns lastchangedate if any and count of items changed after passed date.Date should be in milliseconds."""
    def getItemsCountForDateRange(self,fromDate,toDate):
        """Returns count for items for passed date params.Date should be in milliseconds."""
    def getItemIDsForDateRange(self,fromDate,toDate):
        """Returns id and lastchangedate for items between passed dates.Date should be in milliseconds."""
    def getItemsForDateRange(self,fromDate,toDate):
        """Returns items changed between passed dates.Date should be in milliseconds."""
    def getVersionString(self):
        """Returns version string of cyn.in server"""
    def getSpaces(self,parentUID=None):
        """Returns objects of type Space below passed parent UID."""
    def getObjectIds(self,uid):
        """Returns immediate children objects of passed UID."""
    def getUsers(self):
        """Returns list of user ids for cyn.in site."""
    def getViews(self,parentuid=None):
        """Returns objects of type SmartView below passed parent uid if any"""
    def setOwnPassword(self,newpassword):
        """Sets the current user's password"""
    def list_portal_types(self):
        """Returns a list of all known content types, as the standard TypeInfo dict"""
    def getUserRecentItems(self,username="", maxitemcount=5,pagenumber=1):
        """Return the recent updates of only items touched by a user, up to a maximum of maxitemcount items. If the username is not passed, then current logged in user is used."""
    def getUserRecentItems(self,username="", maxitemcount=5,pagenumber=1):
        """Return the recent updates of only items touched by a user, up to a maximum of maxitemcount items. If the username is not passed, then current logged in user is used."""
    def addDiscussion(self,discussiontext,tags=None,contextUID=None,title=""):
        """Adds a discussion item with specified discussiontext,title and tags.
        If contextUID is not specified then discussion is added at /home
        If title is not specified then one will be generated.
        Safe to use with tags passed as well. Tags are a single string that has tags as comma separated list
        """
    def getTags(self):
        """Returns a list of all tags """

class IAdminFunctions(Interface):
    """Interface to the Admin Functions
    """
    def canAdmin():
        """Returns string "yes" if accessing user can admin, else Faults the xmlrpc call
        """

    def registerUser(self,username,email,fullname,notifyUser=False,password=None):
        """Create a user with passed parameters.
            username and email are required minimally.
            If password is not passed then one is generated.
            If notifyUser is set to true then the user will be emailed a link to allow them to set their own password.
        """

    def verifyUser(self,username,code):
        """Checks that the verification code provided is correct for allowing (in a separate call) reset of password"""

    def setPasswordByReset(self,username,password,randomstring):
        """
            Sets a user's password. Does NOT notify the user of this change. Use resetPassword if you want the user to get an email on password change.
        """

    def resetPassword(self,username):
        """
            Resets a user's password, and emails the user a link to allow them to come and change their password.
        """

    def addUserToGroup(self,username,groups=[]):
        """Adds user with passed username to groups specified in groups parameter.
            If groups are not present, they are first created and then the user is assigned to them.
        """

    def removeUserFromGroup(self,username,groups=[]):
        """Removes user with passed username from groups specified in groups parameter.
            If any of the passed groups do not exist, they are skipped silently.
        """

    def editUserProfile(self,username,keyvaluedict):
        """Updates user properties with passed values in key value dict.
            If any of the passed property names do not exist they are skipped silently.
            If the keyvaluedict contains a term with name 'password' the user's password will be set to the value of this term.
        """
    
    def setUserAvatar(self,username,avatarURL):
        """Set's the users avatar by downloading the image from avatarURL"""
    
    def addGroup(self,groupname):
        """Add's the groupname specified. Does not throw an error if the group already exists."""
    
    def removeGroup(self,groupname):
        """Remove's the groupname specified. Returns True if successful or False if the groupname does not exist"""
    
    def deleteItemByUID(self,UID):
        """Delete's an item which has the passed UID. Throws fault if UID does not exist."""
    
    def userExistsByEmail(self,email):
        """Returns true if a user with that email exists, false if not"""
    
class IAnonymousAPI(Interface):
    """Interface to Anonymous callable Functions like forgotPassword
    """
    def forgotPassword(self,username):
        """Sends the username their forgot password email"""
