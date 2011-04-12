from zope.interface import implements
from Products.CMFCore.utils import getToolByName

from Products.fatsyndication.adapters.feedentry import BaseFeedEntry
from Products.fatsyndication.adapters import BaseFeedSource
from Products.fatsyndication.adapters import BaseFeed

from Products.basesyndication.interfaces import IFeedEntry
from Products.basesyndication.interfaces import IFeedSource
from Products.basesyndication.interfaces import IEnclosure

from Products.Archetypes.ExtensibleMetadata import FLOOR_DATE
from Products.Archetypes.config import UUID_ATTR, REFERENCE_CATALOG

from Products.fatsyndication.browser.feed import FeedView as BaseFeedView
import os.path
from zope.component import getMultiAdapter
from Products.Five import BrowserView
from Products.Five.browser.pagetemplatefile \
    import ZopeTwoPageTemplateFile as PageTemplateFile
from Products.basesyndication.interfaces import IFeed

from ubify import cyninv2theme

class CyninFeedView(BaseFeedView):
    
    basepath = os.path.join(os.path.dirname(cyninv2theme.__file__), 
                            'browser')
    atom   = PageTemplateFile(os.path.join(basepath, 'atom.xml.pt'))
    rss    = PageTemplateFile(os.path.join(basepath, 'rss.xml.pt'))        
    itunes = PageTemplateFile(os.path.join(basepath, 'itunes.xml.pt'))
    
class CyninBaseFeed(BaseFeed):
    def getImageURL(self):
        """See IFeed.
        """
        portal_url = getToolByName(self, 'portal_url')()
        return '%s/logo.jpg' % portal_url        

class CyninBaseFeedEntry(BaseFeedEntry):
    """
    """

    # It's only a mixin, so it doesn't fully implement IFeedEntry
    #implements(IFeedEntry)

    def __init__(self, context):
        self.context = context

    def getWebURL(self):
        """See IFeedEntry.
        """
        use_view_action = self.context.portal_url.getPortalObject().portal_properties.site_properties.typesUseViewActionInListings
        url = self.context.evalURL(self.context.portal_type,use_view_action,self.context.absolute_url())
        
        baseurl = ''
        portal_properties = self.context.portal_url.getPortalObject().portal_properties
        site_prop = portal_properties.site_properties
        if hasattr(site_prop,'base_rss_url') and site_prop.base_rss_url <> '':
            baseurl = site_prop.base_rss_url
        
        if baseurl <> '':
            portal_url = getToolByName(self.context, 'portal_url')()
            url = url.replace(portal_url,baseurl)    
        
        return url

    def getTitle(self):
        """See IFeedEntry.
        """
        return self.context.Title()

    def getDescription(self):
        """See IFeedEntry.
        """
        return self.context.Description()

    def getBody(self):
        """The raw body content of this entry.

        TODO: This needs some thinkwork. RSS accepts all sorts of
        stuff, but Atom is capable of including xhtml without needing
        to resort to CDATA sections and escaping of tags.

        See also getXthml, which should solve this.
        """
        if hasattr(self.context,'CookedBody'):
            return self.context.CookedBody()
        else:
            return self.context.Description()
        
    def getXhtml(self):
        """The (x)html body content of this entry, or None
        """
        pass
        
    def getUID(self):
        """See IFeedEntry.
        """
        uid = getattr(self.context, UUID_ATTR, None)
        if uid is None:
            refcat = getToolByName(self.context, REFERENCE_CATALOG)
            uid = refcat._getUUIDFor(self.context)
        else:
            uid = self.context.UID()
        
        return uid

    def getAuthor(self):
        """See IFeedEntry.
        """
        creator = self.context.Creator()
        member = self.context.portal_membership.getMemberById(creator)
        return member and member.getProperty('fullname') or creator

    def getEffectiveDate(self):
        """See IFeedEntry.
        """
        effective = self.context.modified()
        return effective

    def getModifiedDate(self):
        """See IFeedEntry.
        """
        return self.context.modified()

    def getTags(self):
        """See IFeedEntry.
        """
        return self.context.Subject()

    def getRights(self):
        """See IFeedEntry.
        """
        # XXX Implement me properly!
        # self.context.Rights() ??
        return ''

    def getEnclosure(self):
        """See IFeedEntry.
        """
        # Override this method if you want to do podcasting.        
        if self.__provides__(IEnclosure):
            encobj = BaseEnclosure(self.context)
            return encobj
        else:
            return None
        

class BaseEnclosure:
    implements(IEnclosure)
    
    def __init__(self, context):
        self.context = context
    
    def getURL(self):
        url = self.context.absolute_url()
        
        baseurl = ''
        portal_properties = self.context.portal_url.getPortalObject().portal_properties
        site_prop = portal_properties.site_properties
        if hasattr(site_prop,'base_rss_url') and site_prop.base_rss_url <> '':
            baseurl = site_prop.base_rss_url
        
        if baseurl <> '':
            portal_url = getToolByName(self.context, 'portal_url')()
            url = url.replace(portal_url,baseurl)
            
        return url

    def getLength(self):
        return self.context.getObjSize(self.context)

    def __len__(self):
        return self.context.getObjSize(self.context)

    def getMajorType(self):
        ctype = self.getType()
        return ctype.split("/")[0]

    def getMinorType(self):
        ctype = self.getType()
        return ctype.split("/")[1]

    def getType(self):        
        return self.context.get_content_type()
    
class DocumentFeedEntry(CyninBaseFeedEntry):
    implements(IFeedEntry)

class SiteFeed(CyninBaseFeed):
    pass

class ContentRootFeedSource(BaseFeedSource):
    implements(IFeedSource)

    def getFeedEntries(self, max_only=True):
        if max_only:
            num_of_entries = self.getMaxEntries()
        else:
            num_of_entries = 0 # signals to fetch _all_ items
        brains = self.context.getEntries(num_of_entries)

		### Added checking if there is a getObject() method, else
		### sending just the brain
        if len(brains) > 0 and hasattr(brains[0],'getObject'):
            return [IFeedEntry(brain.getObject()) for brain in brains]
        else:
            return [IFeedEntry(brain) for brain in brains]
    
    getSortedFeedEntries = getFeedEntries
    
class TopicFeed(CyninBaseFeed):
    pass

class TopicFeedSource(BaseFeedSource):
    implements(IFeedSource)
    
    def getFeedEntries(self, max_only=True):
        if max_only:
            num_of_entries = self.getMaxEntries()
        else:
            num_of_entries = 0 # signals to fetch _all_ items
        brains = self.context.getEntries(num_of_entries)
        return [IFeedEntry(brain.getObject()) for brain in brains]
    
    getSortedFeedEntries = getFeedEntries

class ATContentTypeFeedSource(BaseFeedSource):
    implements(IFeedSource)

    def getFeedEntries(self):
        """See IFeedSource
        """        
        d_tool = getToolByName(self.context, 'portal_discussion')
        contobj = self.context
        replies = []
        if contobj.isDiscussable():        
            def getRs(obj, replies, counter):
                rs = d_tool.getDiscussionFor(obj).getReplies()
                if len(rs) > 0:
                    rs.sort(lambda x, y: cmp(x.modified(), y.modified()))
                    for reply in rs:
                        replies.append(IFeedEntry(reply))
                        getRs(reply, replies, counter=counter + 1)
            getRs(contobj, replies, 0)
                
            #replies = [IFeedEntry(reply) for reply in discussion.getReplies()]
            return [IFeedEntry(self.context)] + replies
        else:
            return [IFeedEntry(self.context)]
        
    getSortedFeedEntries = getFeedEntries
    
class ATDocumentFeed(CyninBaseFeed):
    pass

class ATDocumentFeedSource(ATContentTypeFeedSource):    
    pass
    
class ATDocumentFeedEntry(CyninBaseFeedEntry):
    implements(IFeedEntry)
    
class BlogEntryFeed(CyninBaseFeed):
    pass

class BlogEntryFeedSource(ATContentTypeFeedSource):    
    pass
    
class BlogEntryFeedEntry(CyninBaseFeedEntry):
    implements(IFeedEntry)
    
class ATImageFeed(CyninBaseFeed):
    pass

class ATImageFeedSource(ATContentTypeFeedSource):    
    pass
    
class ATImageFeedEntry(CyninBaseFeedEntry):
    implements(IFeedEntry,IEnclosure)
    
class ATLinkFeed(CyninBaseFeed):
    pass

class ATLinkFeedSource(ATContentTypeFeedSource):    
    pass
    
class ATLinkFeedEntry(CyninBaseFeedEntry):
    implements(IFeedEntry)
    
class ATFileFeed(CyninBaseFeed):
    pass

class ATFileFeedSource(ATContentTypeFeedSource):    
    pass
    
class ATFileFeedEntry(CyninBaseFeedEntry):
    implements(IFeedEntry,IEnclosure)
  
class ATEventFeed(CyninBaseFeed):
    pass

class ATEventFeedSource(ATContentTypeFeedSource):    
    pass
    
class ATEventFeedEntry(CyninBaseFeedEntry):
    implements(IFeedEntry)
  
class VideoFeed(CyninBaseFeed):
    pass

class VideoFeedSource(ATContentTypeFeedSource):    
    pass
    
class VideoFeedEntry(CyninBaseFeedEntry):
    implements(IFeedEntry,IEnclosure)

class StatuslogItemFeed(CyninBaseFeed):
    pass

class StatuslogItemFeedSource(ATContentTypeFeedSource):    
    pass
    
class StatuslogItemFeedEntry(CyninBaseFeedEntry):
    implements(IFeedEntry)
    
class DiscussionFeed(CyninBaseFeed):
    pass

class DiscussionFeedSource(ATContentTypeFeedSource):    
    pass
    
class DiscussionFeedEntry(CyninBaseFeedEntry):
    implements(IFeedEntry)
    
class AudioFeed(CyninBaseFeed):
    pass

class AudioFeedSource(ATContentTypeFeedSource):    
    pass
    
class AudioFeedEntry(CyninBaseFeedEntry):
    implements(IFeedEntry,IEnclosure)
