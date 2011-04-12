from Acquisition import aq_base, aq_parent
from zope import interface
from OFS.ObjectManager import ObjectManager

def update_portal_for_z210(portal):
    """The way that the component registry and other things changed when going
    from Zope 2.9 to 2.10.  This function will migrate all aspects that it
    can migrate.
    """

    portal = aq_base(portal)
    if 'utilities' in portal.objectIds():
        for id, u in portal.utilities.objectItems():
            pieces = id.split('-')
            ifacename = pieces[0]
            name = u''
            if len(pieces) > 1:
                name = pieces[1]
            iface = None
            for checkiface in interface.providedBy(u).flattened():
                if checkiface.getName() == ifacename:
                    iface = checkiface
                    break
            if iface is not None:
                update_utility(portal, id, u, iface, name)

        if len(portal.utilities.objectIds()) == 0:
            # using ObjectManager since it doesn't do as intensive
            # security checks as PloneSite.manage_delObjects
            ObjectManager.manage_delObjects(portal, ['utilities'])

def update_utility(newsite, id, utility, iface, name=u''):
    """Take the given utility having come from a pre-zope2.10 based
    site, register it with the new site, and delete it from the old
    site.
    """

    sm = newsite.getSiteManager()
    sm.registerUtility(utility, iface, name=name)
    parent = aq_parent(utility)
    parent.manage_delObjects([id])
