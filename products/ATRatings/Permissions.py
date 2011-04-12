from Products.CMFCore.permissions import setDefaultRoles

ADD_RATING_PERMISSION = 'ATRatings: Add rating'

setDefaultRoles(ADD_RATING_PERMISSION, ( 'Manager', 'Owner', 'Authenticated') )
