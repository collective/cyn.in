from Interface import Interface

class IRatingStorage(Interface):
    """ """

    def addRating(rating, uid, username):
        """Add a rating to an object for the specified user"""

    def deleteRating(uid, username):
        """Delete the user's rating for the specified object"""

    def getUserRating(uid, username):
        """Get a user's rating for the specified object"""

    def deleteRatingsFor(uid):
        """Delete all ratings for the specified object"""
        
    def addHit(uid):
        """Increment the hits for the specified object"""

    # summary statistics
    def getHitCount(self, uid):
        """Get an estimate of the current # of hits/time period for a content object"""

    def getHitRate(self, uid):
        """Get an estimate of the current # of hits/time period for a content object"""

    def getTotalHitCount(self):
        """Get the total number of hits for all content objects combined"""

    def getRatingCount(uid):
        """Get a count of ratings for a particular content object"""
    
    def getRatingSum(uid):
        """Get the sum of ratings for a particular content object"""
    
    def getRatingSumSquared(uid):
        """Get the sum of ratings squared for a particular content object"""
    
    def getRatingMean(uid):
        """Get the mean of ratings for a particular content object"""
    
    def getRatingStdDev(uid):
        """Get the standard deviation of ratings for a particular content object"""

    def getRatingVariance(uid):
        """Get the variance of ratings for a particular content object"""

    def getTotalRatingCount():
        """Get the total number of ratings for all objects"""

    def getRatingMeanCount():
        """Get the count of rating means"""
    
    def getRatingMeanSum():
        """Get the sum of rating means"""
    
    def getRatingMeanSumSquared():
        """Get the sum of rating means squared"""
    
    def getRatingMeanMean():
        """Get the mean of rating means"""
    
    def getRatingMeanStdDev():
        """Get the standard deviation of rating means"""

    def getRatingMeanVariance():
        """Get the variance of rating means"""

    def getNoiseVariance():
        """Get an estimate of the variability of user ratings"""