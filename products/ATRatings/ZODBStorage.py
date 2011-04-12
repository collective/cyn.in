import math
import time
from AccessControl import ClassSecurityInfo
from Acquisition import Implicit
from BTrees.OOBTree import OOBTree
from Globals import InitializeClass
from Persistence import Persistent
from Products.CMFCore.utils import getToolByName
from references import RatingsReference
from IRatingStorage import IRatingStorage

HITS_SUMMARY_ID = '_hits'
RATINGS_SUMMARY_ID = '_ratings'

from config import HIT_RATE_TIME_INTERVAL

class ZODBHitsSummary(Persistent):
    def __init__(self):
        self.hits = 0
        self.hit_rate = 0.0
        self.last_hit_time = time.time()
        
    def addHit(self):
        self.hits += 1
        self.hit_rate = 1.0 + math.exp((time.time() - self.last_hit_time)/float(HIT_RATE_TIME_INTERVAL))*self.hit_rate
        self.last_hit_time = time.time()

    def getLastHitTime(self):
        return self.last_hit_time
    
    def getCount(self):
        return self.hits

    def getHitRate(self):
        # H is a weighted sum of the hits that provides an estimate of the 
        # current hit rate.
        # 
        # If hits occur at t_0, t_1, t_2, etc, H at time t is given by
        # 
        # H(t) = exp((t_0-t)/k) + exp((t_1-t)/k) + exp((t_2-t)/k) + ...
        # 
        # for a specified decay constant k.  We can express H recursively as
        # 
        # H(t_n) = 1 + exp((t_{n-1}-t_n)/k) H(t_{n-1})
        # 
        # To get an idea of what H(t) means, consider the case in which hits
        # occur at intervals of time d, i.e. t_n = n d.  Then
        # 
        # H(t_n) = Sum_{j=0}^n exp(-j d/k), so as n->\infinity, we have
        # H -> 1/(1-exp(-d/k))
        #
        # Now for d << k, we have exp(-d/k) \approx 1-d/k, so H -> k/d
        # 
        # If k is, say, 1 week, then H -> the # of hits/week
        #
        # Basically H will be a rough estimate of the current hit rate, since
        # more weight is given to recent events.
        return math.exp((time.time() - self.last_hit_time)/float(HIT_RATE_TIME_INTERVAL))*self.hit_rate


class ZODBRatingsSummary(Persistent):
    # summary of ratings for an object
    # count = # of ratings
    # sum = sum of ratings
    # sum_squared = sum of (ratings squared)

    def __init__(self):
        self.count = 0
        self.sum = 0
        self.sum_squared = 0

    def getCount(self):
        return self.count
    
    def getSum(self):
        return self.sum
    
    def getSumSquared(self):
        return self.sum_squared
        
    def getMean(self):
        if self.count == 0:
            return None
        return float(self.sum)/float(self.count)
    
    def getStdDev(self):
        v = self.getVariance()
        if v is None:
            return None
        return math.sqrt(v)

    def getVariance(self):
        if self.count == 0:
            return None
        mean = self.getMean()
        return float(self.sum_squared)/float(self.count) - mean*mean
    

class ZODBRatingsMeanSummary(ZODBRatingsSummary):
    # summary of means of ratings for all objects
    # total_count = # of ratings for all objects
    # count = # of mean ratings
    # sum = sum of mean ratings
    # sum_squared = sum of (mean ratings squared)
    
    def __init__(self):
        ZODBRatingsSummary.__init__(self)
        self.total_count = 0
        self.squared_deviation_sum = 0
        
    def getTotalCount(self):
        return self.total_count
    
    def getNoiseVariance(self):
        # return an estimate of rating noise variance
        if self.total_count - self.count == 0:
            return None
        return self.squared_deviation_sum / (self.total_count - self.count)
    

class ZODBRatings(Persistent):
    # Manage ratings for a single object

    def __init__(self):
        self.repository = OOBTree()
        self.repository[RATINGS_SUMMARY_ID] = ZODBRatingsSummary()
        self.repository[HITS_SUMMARY_ID] = ZODBHitsSummary()

    def _getHitsSummary(self):
        return self.repository[HITS_SUMMARY_ID]

    def _getRatingsSummary(self):
        return self.repository[RATINGS_SUMMARY_ID]

    def addHit(self):
        return self._getHitsSummary().addHit()

    def getHitCount(self):
        return self._getHitsSummary().getCount()

    def getHitRate(self):
        return self._getHitsSummary().getHitRate()

    def addRating(self, rating, username):
        assert not self.repository.has_key(username)
        self.repository[username] = rating
        summary = self.repository[RATINGS_SUMMARY_ID]
        summary.count += 1
        summary.sum += rating
        summary.sum_squared += rating * rating
        self._p_changed = 1
    
    def deleteRating(self, username):
        rating = self.repository[username]
        summary = self.repository[RATINGS_SUMMARY_ID]
        summary.count -= 1
        summary.sum -= rating
        summary.sum_squared -= rating*rating
        del self.repository[username]
        self._p_changed = 1

    def getUserRating(self, username):
        return self.repository.get(username, None)

    # summary stats
    def getRatingCount(self):
        return self._getRatingsSummary().getCount()
    
    def getSum(self):
        return self._getRatingsSummary().getSum()
    
    def getSumSquared(self):
        return self._getRatingsSummary().getSumSquared()
    
    def getMean(self):
        return self._getRatingsSummary().getMean()
    
    def getStdDev(self):
        return self._getRatingsSummary().getStdDev()
    
    def getVariance(self):
        return self._getRatingsSummary().getVariance()


class ZODBStorage(Implicit):
    # Manage ratings for all objects
    
    __implements__ = IRatingStorage
    
    security = ClassSecurityInfo()
    repository = None


    def __init__(self):
        self.repository = OOBTree()
        self.repository[RATINGS_SUMMARY_ID] = ZODBRatingsMeanSummary()
        self.repository[HITS_SUMMARY_ID] = ZODBHitsSummary()
        
    def _getRepository(self):
        return self.repository

    def _getObjectRatings(self, uid, createFlag=1):
        """ create a new ratings when use createFlag """
        repository = self._getRepository()
        ratings = repository.get(uid, None)
        if ratings is None and createFlag:
            repository[uid] = ZODBRatings()
            ratings = repository[uid]
            
            reference_catalog = getToolByName(self, 'reference_catalog')
            object = reference_catalog.lookupObject(uid)
            ratings_tool = getToolByName(self, 'portal_ratings')
            reference_catalog.addReference(object, ratings_tool, 'HasRatings', RatingsReference)

        return ratings

    def _getHitsSummary(self):
        return self.repository[HITS_SUMMARY_ID]

    def _getRatingsSummary(self):
        return self.repository[RATINGS_SUMMARY_ID]

    def addRating(self, rating, uid, username):
        summary = self.repository[RATINGS_SUMMARY_ID]
        summary.total_count += 1
        
        ratings = self._getObjectRatings(uid)
        mean = ratings.getMean()
        if mean is not None:
            summary.squared_deviation_sum -= summary.count * summary.getVariance()
            summary.count -= 1
            summary.sum -= mean
            summary.sum_squared -= mean * mean

        ratings.addRating(rating, username)

        mean = ratings.getMean()
        summary.count += 1
        summary.sum += mean
        summary.sum_squared += mean * mean
        summary.squared_deviation_sum += summary.count * summary.getVariance()

    def deleteRating(self, uid, username):
        summary = self.repository[RATINGS_SUMMARY_ID]
        summary.total_count -= 1
        ratings = self._getObjectRatings(uid)
        mean = ratings.getMean()
        summary.squared_deviation_sum -= summary.count * summary.getVariance()
        summary.count -= 1
        summary.sum -= mean
        summary.sum_squared -= mean * mean

        ratings.deleteRating(username)

        mean = ratings.getMean()
        if mean is not None:
            summary.count += 1
            summary.sum += mean
            summary.sum_squared += mean * mean
            summary.squared_deviation_sum += summary.count * summary.getVariance()

    def getUserRating(self, uid, username):
        ratings = self._getObjectRatings(uid, 0)
        return ratings and ratings.getUserRating(username)

    def deleteRatingsFor(self, uid):
        repository = self._getRepository()
        try:
            del repository[uid]
        except:
            # maybe not stored at all
            pass
        
    def addHit(self, uid):
        self._getHitsSummary().addHit()
        return self._getObjectRatings(uid).addHit()

    # summary stats
    def getHitCount(self, uid):
        ratings = self._getObjectRatings(uid, 0)
        return ratings and ratings.getHitCount()

    def getHitRate(self, uid):
        ratings = self._getObjectRatings(uid, 0)
        return ratings and ratings.getHitRate()

    def getRatingCount(self, uid):
        # return a count of ratings for a particular content object
        ratings = self._getObjectRatings(uid, 0)
        return ratings and ratings.getRatingCount()
    
    def getSum(self, uid):
        # return a sum of ratings for a particular content object
        ratings = self._getObjectRatings(uid, 0)
        return ratings and ratings.getSum()
    
    def getSumSquared(self, uid):
        # return a sum of ratings squared for a particular content object
        ratings = self._getObjectRatings(uid, 0)
        return ratings and ratings.getSumSquared()
    
    def getMean(self, uid):
        # return the mean of ratings for a particular content object
        ratings = self._getObjectRatings(uid, 0)
        return ratings and ratings.getMean()
    
    def getStdDev(self, uid):
        # return the standard deviation of ratings for a particular content object
        ratings = self._getObjectRatings(uid, 0)
        return ratings and ratings.getStdDev()

    def getVariance(self, uid):
        # return the standard deviation of ratings for a particular content object
        ratings = self._getObjectRatings(uid, 0)
        return ratings and ratings.getVariance()

    def getTotalHitCount(self):
        return self._getHitsSummary().getCount()

    def getTotalRatingCount(self):
        # return a count of rating means
        return self._getRatingsSummary().getTotalCount()

    def getRatingMeanCount(self):
        # return a count of rating means
        return self._getRatingsSummary().getCount()
    
    def getRatingMeanSum(self):
        # return a sum of rating means
        return self._getRatingsSummary().getSum()
    
    def getRatingMeanSumSquared(self):
        # return a sum of rating means squared
        return self._getRatingsSummary().getSumSquared()
    
    def getRatingMeanMean(self):
        # return a mean of rating means
        return self._getRatingsSummary().getMean()
    
    def getRatingMeanStdDev(self):
        # return a standard deviation of rating means
        return self._getRatingsSummary().getStdDev()

    def getRatingMeanVariance(self):
        # return a standard deviation of rating means
        return self._getRatingsSummary().getVariance()

    def getNoiseVariance(self):
        return self._getRatingsSummary().getNoiseVariance()
    
InitializeClass(ZODBStorage)
