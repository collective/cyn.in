from AccessControl import ClassSecurityInfo
from Globals import InitializeClass
from Acquisition import aq_parent
from AccessControl import Unauthorized

from Products.CMFCore.utils import getToolByName
from Products.CMFCore import CMFCorePermissions
from Products.CMFCore.PortalFolder import PortalFolder

from Products.Archetypes.public import Schema
from Products.Archetypes.public import IntegerField, IntDisplayList
from Products.Archetypes.public import SelectionWidget

# constants for enableConstrainMixin
ACQUIRE = 0 # acquire locallyAllowedTypes from parent (default)
DISABLED = -1 # use default behavior of PortalFolder which uses the FTI information
ENABLED  = 1 # allow types from locallyAllowedTypes only

enableDisplayList = IntDisplayList((
    (ACQUIRE,  'Use setting from parent folder', 'ratings_aquire_parent'),
    (DISABLED, 'Disable', 'ratings_disable'),
    (ENABLED,  'Enable', 'ratings_enable'),
    ))

RatingsFolderMixinSchema = Schema((
    IntegerField('enableRatings',
        default=ACQUIRE,
        vocabulary = enableDisplayList,
        accesor = 'getEnableRatings', 
        edit_accessor = 'getEnableRatings', 
        mutator = 'setEnableRatings',
        write_permissions='Manage properties',
        schemata='Ratings',
        languageIndependent = True,
        widget=SelectionWidget(
            label='Enable ratings',
            visible = {'edit': 'visible', 'view': 'hidden'},
            label_msgid='label_enable_ratings',
            description='Enable raings under this folder',
            description_msgid='description_enable_ratings',
            i18n_domain='at_ratings')
        ),
    IntegerField('enableCountings',
        default=ACQUIRE,
        vocabulary = enableDisplayList,
        accesor = 'getEnableCountings',
        edit_accessor = 'getEnableCountings',
        mutator = 'setEnableCountings',
        write_permissions='Manage properties',
        schemata='Ratings',
        languageIndependent = True,
        widget=SelectionWidget(
            label='Enable click countings',
            visible = {'edit': 'visible', 'view': 'hidden'},
            label_msgid='label_enable_countings',
            description='Enable click countings under this folder',
            description_msgid='description_enable_countings',
            i18n_domain='at_ratings')
        ),

    ))

class RatingsFolderMixin:

    def _getEnableProperty(self, propertyName):
        value = self.getProperty(propertyName, ACQUIRE)
        if value is True:
            return ENABLED
        elif value is False:
            return DISABLED
        return value

    def _setEnableProperty(self, propertyName, value):
        # backward compatible
        if not self.hasProperty(propertyName) and \
              hasattr(self.aq_base, propertyName):
           delattr(self, propertyName)

        value = int(value)
        if value != ACQUIRE:
            pValue = (value == ENABLED)
            if not self.hasProperty(propertyName):
                self.manage_addProperty(propertyName, pValue, 'boolean') 
            else:
                self.manage_changeProperties({propertyName:pValue})

        # acquire
        elif self.hasProperty(propertyName):
            self.manage_delProperties(ids=[propertyName])

    def getEnableRatings(self):
        """ """
        return self._getEnableProperty('enableRatings')

    def setEnableRatings(self, value):
        """ """
        self._setEnableProperty('enableRatings', value)

    def getEnableCountings(self):
        """ """
        return self._getEnableProperty('enableCountings')

    def setEnableCountings(self, value):
        """ """
        self._setEnableProperty('enableCountings', value)

InitializeClass(RatingsFolderMixin)


