import logging
logger = logging.getLogger('p4a.z2utils.patches')

def apply_patches():
    _apply_getSubObject_patch()
    _apply_DynamicView_patch()

def unapply_patches():
    _unapply_getSubObject_patch()
    _unapply_DynamicView_patch()

def _unapply_getSubObject_patch():
    import Products.Archetypes
    patched = getattr(Products.Archetypes, '_p4a_z2utils_patched', False)
    if patched:
        from Products.Archetypes.BaseObject import BaseObject
        BaseObject.getSubObject = BaseObject.__p4a_z2utils_orig_getSubObject
        del BaseObject.__p4a_z2utils_orig_getSubObject
        del Products.Archetypes._p4a_z2utils_patched
        return True
    return False

def _unapply_DynamicView_patch():
    import Products.CMFDynamicViewFTI
    patched = getattr(Products.CMFDynamicViewFTI, '_p4a_z2utils_patched', False)
    if patched:
        from Products.CMFDynamicViewFTI.fti import DynamicViewTypeInformation
        from Products.CMFDynamicViewFTI.browserdefault import \
             BrowserDefaultMixin

        DynamicViewTypeInformation.getAvailableViewMethods = \
            DynamicViewTypeInformation. \
                __p4a_z2utils_orig_getAvailableViewMethods
        DynamicViewTypeInformation.getDefaultViewMethod = \
            DynamicViewTypeInformation.__p4a_z2utils_orig_getDefaultViewMethod
        BrowserDefaultMixin.getAvailableLayouts = \
            BrowserDefaultMixin.__p4a_z2utils_orig_getAvailableLayouts

        del DynamicViewTypeInformation. \
            __p4a_z2utils_orig_getAvailableViewMethods
        del DynamicViewTypeInformation.__p4a_z2utils_orig_getDefaultViewMethod
        del BrowserDefaultMixin.__p4a_z2utils_orig_getAvailableLayouts

        del Products.CMFDynamicViewFTI._p4a_z2utils_patched

        return True
    return False

def _apply_getSubObject_patch():
    """Apply a patch to AT < 1.4 so that traversal checks for data
    object first, then zope 3 view, then acquired attributes.
    """

    try:
        # don't patch if Archetypes isn't present
        from Products import Archetypes
    except:
        return

    # make sure we don't patch something that's already been patched
    patched = getattr(Archetypes, '_p4a_z2utils_patched', False)
    if patched:
        return

    try:
        from Products.Archetypes import bbb
        # the bbb module is included with AT 1.4 and higher where we do
        # not want this monkey patch to be in effect
        return
    except ImportError, e:
        pass

    logger.info("Fixing Archetypes Zope 3 traversal.")

    from Products.Archetypes.BaseObject import BaseObject
    from zope.app.publication.browser import setDefaultSkin
    from zope.app.traversing.interfaces import ITraverser, ITraversable
    from zope.component import getMultiAdapter, ComponentLookupError
    from zope.publisher.interfaces.browser import IBrowserRequest
    from Products.Five.traversable import FakeRequest
    import Products.Five.security
    from zExceptions import NotFound

    BaseObject.__p4a_z2utils_orig_getSubObject = BaseObject.getSubObject

    def getSubObject(self, name, REQUEST, RESPONSE=None):
        obj = self.__p4a_z2utils_orig_getSubObject(name, REQUEST, RESPONSE)
        if obj is not None:
            return obj

        # The following is a copy from Five's __bobo_traverse__ stuff,
        # see Products.Five.traversable for details.
        # Basically we're forcing Archetypes to look up the correct
        # Five way:
        #   1) check for data object first
        #   2) check for zope3 view 
        #   3) return nothing so that AT's default __bobo_traverse__ will use aq

        if not IBrowserRequest.providedBy(REQUEST):
            # Try to get the REQUEST by acquisition
            REQUEST = getattr(self, 'REQUEST', None)
            if not IBrowserRequest.providedBy(REQUEST):
                REQUEST = FakeRequest()
                setDefaultSkin(REQUEST)

        # Con Zope 3 into using Zope 2's checkPermission
        Products.Five.security.newInteraction()

        # Use the ITraverser adapter (which in turn uses ITraversable
       # adapters) to traverse to a view.  Note that we're mixing
        # object-graph and object-publishing traversal here, but Zope
        # 2 has no way to tell us when to use which...
        # TODO Perhaps we can decide on object-graph vs.
        # object-publishing traversal depending on whether REQUEST is
        # a stub or not?
        try:
            return ITraverser(self).traverse(
                path=[name], request=REQUEST).__of__(self)
        except (ComponentLookupError, LookupError, TypeError,
                AttributeError, KeyError, NotFound):
            pass

        return None

    BaseObject.getSubObject = getSubObject

    Archetypes._p4a_z2utils_patched = True

def _apply_DynamicView_patch():
    """Enable CMFDynamicViewFTI to pull the available/default view(s) from
    adapters.
    """

    try:
        # don't patch if CMFDynamicViewFTI is not available
        from Products import CMFDynamicViewFTI
    except:
        return

    # make sure we don't patch something that's already been patched
    patched = getattr(CMFDynamicViewFTI, '_p4a_z2utils_patched', False)
    if patched:
        return

    # here's hoping that the current version of CMFDynamicViewFTI has
    # already had this code integrated into core 
    from Products.CMFDynamicViewFTI import interfaces
    if hasattr(interfaces, 'IDynamicallyViewable'):
        return

    logger.info("Extending CMFDynamicViewFTI's dynamic view support "
                "with interfaces.")

    from zope.interface import Interface

    class IDynamicallyViewable(Interface):

        def getDefaultViewMethod():
            """Get the name of the default view method
            """

        def getAvailableViewMethods():
            """Get a tuple of registered view method names
            """

        def getAvailableLayouts(self):
            """Get the layouts for this object

            Returns tuples of tuples of view name + title.
            """

    from Products.CMFDynamicViewFTI.fti import DynamicViewTypeInformation
    from Products.CMFDynamicViewFTI.browserdefault import BrowserDefaultMixin

    DynamicViewTypeInformation.__p4a_z2utils_orig_getAvailableViewMethods = (
        DynamicViewTypeInformation.getAvailableViewMethods.im_func)
    DynamicViewTypeInformation.__p4a_z2utils_orig_getDefaultViewMethod = (
        DynamicViewTypeInformation.getDefaultViewMethod.im_func)
    BrowserDefaultMixin.__p4a_z2utils_orig_getAvailableLayouts = (
        BrowserDefaultMixin.getAvailableLayouts.im_func)

    def getDefaultViewMethod(self, context):
        """Get the default view method from the FTI
        """
        adapter = IDynamicallyViewable(context, None)
        if adapter is not None:
            return adapter.getDefaultViewMethod()

        return DynamicViewTypeInformation. \
               __p4a_z2utils_orig_getDefaultViewMethod(self, context)

    def getAvailableViewMethods(self, context):
        """Get a tuple of registered view methods
        """
        adapter = IDynamicallyViewable(context, None)
        if adapter is not None:
            return adapter.getAvailableViewMethods()

        return DynamicViewTypeInformation \
               .__p4a_z2utils_orig_getAvailableViewMethods(self, context)

    def getAvailableLayouts(self):
        """Get the layouts registered for this object
        """
        adapter = IDynamicallyViewable(self, None)
        if adapter is not None:
            return adapter.getAvailableLayouts()

        return BrowserDefaultMixin \
               .__p4a_z2utils_orig_getAvailableLayouts(self)

    DynamicViewTypeInformation.getAvailableViewMethods = getAvailableViewMethods
    DynamicViewTypeInformation.getDefaultViewMethod = getDefaultViewMethod
    BrowserDefaultMixin.getAvailableLayouts = getAvailableLayouts

    interfaces.IDynamicallyViewable = IDynamicallyViewable

    CMFDynamicViewFTI._p4a_z2utils_patched = True
