import os, sys
import urllib
import Globals
from AccessControl import ClassSecurityInfo
from DateTime import DateTime
from OFS.SimpleItem import SimpleItem
from Acquisition import aq_base

from Products.Archetypes.Referenceable import Referenceable
from OFS.PropertyManager import PropertyManager
from Products.CMFCore.utils import UniqueObject, getToolByName
from Products.CMFPlone.PloneBaseTool import PloneBaseTool
from Products.PageTemplates.PageTemplateFile import PageTemplateFile

# lazy way of configuring this tool
from config import MIN_RATING_VALUE, MAX_RATING_VALUE, STORAGE_CLASS, STORAGE_ARGS, NEUTRAL_RATING_VALUE
from Permissions import ADD_RATING_PERMISSION
from Products.CMFCore.permissions import ManagePortal

from ZODBStorage import HITS_SUMMARY_ID, RATINGS_SUMMARY_ID
# ##############################################################################
class RatingsTool(PloneBaseTool, UniqueObject, SimpleItem, Referenceable, PropertyManager):
    """ """
    id = 'portal_ratings'
    meta_type= 'Ratings Tool'
#    toolicon = 'skins/plone_images/favorite_icon.gif'
    security = ClassSecurityInfo()
    isPrincipiaFolderish = 0
    storage = None

    __implements__ = (PloneBaseTool.__implements__, SimpleItem.__implements__, )

    manage_options = ( ({'label':'Overview', 'action':'manage_overview'},) +
                       PropertyManager.manage_options + SimpleItem.manage_options)

    security.declareProtected(ManagePortal, 'manage_overview')
    manage_overview = PageTemplateFile('www/portal_ratings_manage_overview', globals())
    manage_overview.__name__ = 'manage_overview'
    manage_overview._need__name__ = 0

    manage_main = manage_overview

    _properties = PropertyManager._properties + (
        {'id':'allowed_rating_types', 'type': 'lines', 'mode':'w',
         'label':'Allowed raing types'},
        {'id':'allowed_counting_types', 'type': 'lines', 'mode':'w',
         'label':'Allowed hit counting types'},
        )

    allowed_rating_types = ['Document', 'News Item', 'File', 'Image', 'Link', ]
    allowed_counting_types = ['Document', 'News Item', 'File', 'Image', 'Link', ]

    def isRatingAllowedFor(self, content):
        """ do content allow rating?

        Add a 'allowRatings' boolean property to the context to enable it"""
        allowRatings = getattr(content, 'enableRatings', 1)
        if not allowRatings:
            return 0
        if content.getPortalTypeName() not in self.allowed_rating_types:
            return 0
        return hasattr(aq_base(content), 'UID')

    def isCountingAllowedFor(self, content):
        """ do the content allow hit count

        Add a 'allowCountings' boolean property to the context to enable it"""
        allowCountings = getattr(content, 'enableCountings', 0)
        if not allowCountings:
            return 0
        if content.getPortalTypeName() not in self.allowed_counting_types:
            return 0
        return hasattr(aq_base(content), 'UID')
    
    security.declarePublic('getCyninRating')
    def getCyninRating(self,uid):
        cyninrating = self._getCyninRating(uid)
        if cyninrating is None:            
            return None
        else:
            return cyninrating
        
    security.declarePublic('getCyninRatingCount')
    def getCyninRatingCount(self,uid):
        return self._getCyninRatingCount(uid)
    
    security.declarePublic('getTopRatingsAll')
    def getTopRatingsAll(self,brains):
        """ get top n hot contents from catalog brains """
        results = []
        for brain in brains:
            value = self._getCyninRating(brain.UID)            
            if value <> None:
                ratecount = self.getRatingCount(brain.UID)
                cyninratingcount = self._getCyninRatingCount(brain.UID)
                results.append( (value, brain, ratecount, cyninratingcount))
        
        def sortlist(x,y):
            if cmp(y[0],x[0]) != 0:
                return cmp(y[0],x[0])
            else:
                return cmp(y[2],x[2])
            
        results.sort(lambda x,y:sortlist(x,y));
        return results
    
    security.declarePublic('getTopRatings')
    def getTopRatings(self,  brains, limit=5):
        """ get top n hot contents from catalog brains """
        results = []
        results = self.getTopRatingsAll(brains)
        return results[:limit]

    security.declarePublic('getBadRatings')
    def getBadRatings(self, brains, limit=5):
        """ get bad ratings from catalog brains """
        results = []
        for brain in brains:
            value = self.getRatingMean(brain.UID)
            if value:
                results.append((value, brain))

        results.sort(lambda x,y:cmp(x[0], y[0]))        
        return results[:limit]

    security.declarePublic('getTopCountings')
    def getTopCountings(self, brains, limit=5):
        """ get top n hot contents from catalog brains """
        results = []
        for brain in brains:
            count = self.getHitCount(brain.UID)
            if count:
                results.append((count, brain))

        results.sort(lambda x,y:cmp(y[0], x[0]))
        return results[:limit]

    security.declarePublic('getBadCountings')
    def getBadCountings(self, brains, limit=5):
        """ get top n cold contents from catalog brains """
        results = []
        for brain in brains:
            count = self.getHitCount(brain.UID)
            if count:
                results.append((count, brain))

        results.sort(lambda x,y:cmp(x[0], y[0]))
        return results[:limit]

    def addRating(self, rating, uid):
        mt = getToolByName(self, 'portal_membership')
        if mt.isAnonymousUser():
            raise ValueError, 'Anonymous user cannot rate content'

        # check permission
        reference_catalog = getToolByName(self, 'reference_catalog')
        object = reference_catalog.lookupObject(uid)
        mt.checkPermission(ADD_RATING_PERMISSION, object)

        member = mt.getAuthenticatedMember()
        username = member.getUserName()

        old_rating = self._getUserRating(uid, username)
        if old_rating is not None:
            self._deleteRating(uid, username)
        return self._addRating(rating, uid, username)

    def getUserRating(self, uid, username=None):
        if username is None:
            mt = getToolByName(self, 'portal_membership')
            if mt.isAnonymousUser():
                raise ValueError, 'Anonymous user cannot rate content'
            member = mt.getAuthenticatedMember()
            username = member.getUserName()
        return self._getUserRating(uid, username)

    def addHit(self, uid):
        self._getStorage().addHit(uid)

    # Summary statistics: HITS

    # hits for individual item
    def getHitCount(self, uid):
        return self._getStorage().getHitCount(uid) or 0

    # hits for all items
    def getTotalHitCount(self):
        return self._getHitsSummary().getCount()

    def getHitRateTimeInterval(self):
        return HIT_RATE_TIME_INTERVAL

    def getHitRate(self, uid):
        return self._getStorage().getHitRate(uid)


    # Summary statistics: RATINGS

    def getMinRating(self):
        return MIN_RATING_VALUE

    def getMaxRating(self):
        return MAX_RATING_VALUE

    # rating stats for individual items
    def getRatingCount(self, uid):
        return self._getStorage().getRatingCount(uid)

    def getRatingSum(self, uid):
        return self._getStorage().getSum(uid)

    def getRatingSumSquared(self, uid):
        return self._getStorage().getSumSquared(uid)

    def getRatingMean(self, uid):
        ratingMean = self._getStorage().getMean(uid)
        if ratingMean == None:
            return 0
        else:
            return ratingMean

    def getRatingStdDev(self, uid):
        return self._getStorage().getStdDev(uid)

    def getRatingVariance(self, uid):
        return self._getStorage().getVariance(uid)

    # rating stats for all items
    def getTotalRatingCount(self):
        """a count of rating means."""
        return self._getStorage().getTotalRatingCount()

    def getRatingMeanCount(self):
        """a count of rating means."""
        return self._getStorage().getRatingMeanCount()

    def getRatingMeanSum(self):
        """return a sum of rating means."""
        return self._getStorage().getRatingMeanSum()

    def getRatingMeanSumSquared(self):
        """a sum of rating means squared."""
        return self._getStorage().getRatingMeanSumSquared()

    def getRatingMeanMean(self):
        """a mean of rating means."""
        return self._getStorage().getRatingMeanMean()

    def getRatingMeanStdDev(self):
        """a standard deviation of rating means."""
        return self._getStorage().getRatingMeanStdDev()

    def getRatingMeanVariance(self):
        """a standard deviation of rating means"""
        return self._getStorage().getRatingMeanVariance()

    def getNoiseVariance(self):
        return self._getStorage().getNoiseVariance()

    def getEstimatedRating(self, uid):
        """Use a Bayesian MMSE estimator for DC in white Gaussian noise to
        estimate the true rating for an item.

        Motivation: a small number of very positive or very negative ratings
        can make an item look much better or worse than it actually is.  We
        use a statistical technique to reduce this kind of small number bias.
        Essentially we assume that true ratings have a Gaussian distribution.
        Most true ratings are somewhere in the middle, with small numbers
        very high and small numbers very low.  User ratings for an item are
        the item's true rating + some Gaussian noise.  User ratings are
        mostly close to the true rating, with a few much higher and a few
        much lower.

        We estimate a prior distribution of true means and the noise level
        from all the data.  We then use this prior info for the Bayesian
        estimator.  See _Fundamentals of Statistical Signal Processing_, by
        Alan Kay, pp. 316 - 321 for details.
        """

        priorMean = self.getRatingMeanMean()
        noiseVariance = self.getNoiseVariance()
        itemMean = self.getRatingMean(uid)

        if priorMean is None or noiseVariance is None:
            # not enough information to compute a prior -- just return the mean
            if itemMean is None:
                # no data for computing a mean -- return the middle rating
                return 0.5 * (float(self.getMinRating()) + float(self.getMaxRating()))
            return itemMean

        if itemMean is None:
            return priorMean

        priorVariance = self.getRatingMeanVariance()

        if priorVariance == 0.0 and noiseVariance == 0.0:
            return itemMean

        itemRatings = self.getRatingCount(uid)

        alpha = priorVariance / (priorVariance + noiseVariance/itemRatings)
        return alpha * itemMean + (1.0 - alpha) * priorMean


    # private interface
    def _getStorage(self):
        if self.storage is None:
            self.storage = STORAGE_CLASS(**STORAGE_ARGS)
        return self.storage

    def _addRating(self, rating, uid, username):
        # delegate to storage
        self._getStorage().addRating(rating, uid, username)

    def _deleteRating(self, uid, username):
        # delegate to storage
        self._getStorage().deleteRating(uid, username)

    def _getUserRating(self, uid, username):
        # delegate to storage        
        return self._getStorage().getUserRating(uid, username)

    def _deleteRatingsFor(self, uid):
        # delegate to storage
        return self._getStorage().deleteRatingsFor(uid)
    
    def _getCyninRating(self,uid):                
        returnvalue = None
        
        objRating = self._getStorage()._getObjectRatings(uid,0)
        if objRating:
            repository = objRating.repository
            keyslist = [k for k in repository.keys() if k not in (HITS_SUMMARY_ID,RATINGS_SUMMARY_ID)]
            if len(keyslist) == 0:
                returnvalue = None
            else:
                returnvalue = 0
            for eachkey in keyslist:
                value = repository.get(eachkey,None)
                if value and isinstance(value,int):                    
                    if value == NEUTRAL_RATING_VALUE:
                        self._deleteRating(uid,eachkey)
                    else:
                        returnvalue = returnvalue + (value - NEUTRAL_RATING_VALUE)
        
        return returnvalue
    
    def _getCyninRatingCount(self,uid):
        result = {'positive':0,'negative':0,'positivescore':0,'negativescore':0}
        
        objRating = self._getStorage()._getObjectRatings(uid,0)
        if objRating:
            repository = objRating.repository
            keyslist = [k for k in repository.keys() if k not in (HITS_SUMMARY_ID,RATINGS_SUMMARY_ID)]
            
            for eachkey in keyslist:
                value = repository.get(eachkey,None)
                if value and isinstance(value,int):                    
                    if value > NEUTRAL_RATING_VALUE:
                        result['positive'] = result['positive'] + 1
                        result['positivescore'] = result['positivescore'] + (value - NEUTRAL_RATING_VALUE)
                    elif value < NEUTRAL_RATING_VALUE:
                        result['negative'] = result['negative'] + 1
                        result['negativescore'] = result['negativescore'] + (value - NEUTRAL_RATING_VALUE)
        
        return result
    
Globals.InitializeClass(RatingsTool)
