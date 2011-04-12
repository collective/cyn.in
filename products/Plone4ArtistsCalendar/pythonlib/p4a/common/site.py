from zope.component.interfaces import ISiteManager
from zope.app.component.hooks import setSite
from zope.app.component.interfaces import ISite, IPossibleSite
from Products.Five.site.localsite import enableLocalSiteHook

def ensure_site(context):
    """Ensure the given context implements ISite.  The importance of
    this method is that it will ensure the given context is an ISite
    regardless of the Zope version (Zope 2.9 had a really hacked up
    SiteManager mechanism we have to account for).

      >>> from zope.app.component.interfaces import ISite, IPossibleSite
      >>> from OFS.Folder import Folder
      >>> if not IPossibleSite.implementedBy(Folder):
      ...    from zope import interface
      ...    from Products.Five.site.metaconfigure import (FiveSite,
      ...                                                  classSiteHook)
      ...    classSiteHook(Folder, FiveSite)
      ...    interface.classImplements(Folder, IPossibleSite)
      >>> om = Folder('foo')

      >>> ISite.providedBy(om)
      False

      >>> ensure_site(om)
      >>> ISite.providedBy(om)
      True

    """

    if not IPossibleSite.providedBy(context):
        if hasattr(context, 'getPhysicalPath'):
            p = '/'.join(context.getPhysicalPath())
        elif hasattr(context, 'getId'):
            p = context.getId()
        elif hasattr(context, 'id'):
            p = id
        else:
            p = str(context)

        raise TypeError('The object, "%s", is not an IPossibleSite' % p)

    if not ISite.providedBy(context):
        enableLocalSiteHook(context)
        setSite(context)

    if not ISite.providedBy(context):
        raise TypeError('Somehow trying to configure "%s" as an ISite '
                        'has failed' % '/'.join(context.getPhysicalPath()))
