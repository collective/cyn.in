import Acquisition
from Products.CMFCore import utils as cmfutils
from zope import interface

try:
    from zope.component.interface import interfaceToName
except ImportError:
    def interfaceToName(context, iface):
        """Return the string representation of the given iface name.

            >>> from zope import interface
            >>> class ITest(interface.Interface): pass
            >>> interfaceToName(None, ITest)
            'p4a.z2utils.utils.ITest'

        """

        # context argument only used to maintain api compatibility with
        # interfaceToName from zope 3.3
        return iface.__module__ + '.' + iface.__name__

def remove_marker_ifaces(context, ifaces): 
    """Remove the given interfaces from all objects using a catalog
    query.  context needs to either be the portal or be properly aq wrapped
    to allow for cmf catalog tool lookup.  ifaces can be either a single
    interface or a sequence of interfaces.

      >>> from zope import interface
      >>> class ITest(interface.Interface): pass
      >>> class Mock(object):
      ...     def __init__(self, id): self.id = id
      ...     def getObject(self): return self
      ...     def __repr__(self): return '<Mock id=%s>' % self.id
      >>> m = Mock('Portal Root')
      >>> objs = [Mock('m1'), Mock('m2'), Mock('m3')]
      >>> interface.directlyProvides(objs[1], ITest)
      >>> m.portal_catalog = lambda **kwargs: objs

      >>> remove_marker_ifaces(m, ITest)
      1

      >>> remove_marker_ifaces(m, [ITest])
      0

    """

    if not isinstance(ifaces, (tuple, list)):
        ifaces = [ifaces]

    count = 0
    for iface in ifaces:
        for obj in objs_with_iface(context, iface):
            count += 1
            provided = interface.directlyProvidedBy(obj)
            interface.directlyProvides(obj, provided - iface)
    return count

def objs_with_iface(context, iface):
    """Return all objects in the system as found by the nearest portal
    catalog that provides the given interface.  The result will be a generator
    for scalability reasons.

      >>> from zope import interface
      >>> class ITest(interface.Interface): pass
      >>> class Mock(object):
      ...     def __init__(self, id): self.id = id
      ...     def getObject(self): return self
      ...     def __repr__(self): return '<Mock id=%s>' % self.id
      >>> m = Mock('Portal Root')
      >>> objs = [Mock('m1'), Mock('m2'), Mock('m3')]
      >>> interface.directlyProvides(objs[1], ITest)
      >>> m.portal_catalog = lambda **kwargs: objs

      >>> [x for x in objs_with_iface(m, ITest)]
      [<Mock id=m2>]

    """

    catalog = cmfutils.getToolByName(context, 'portal_catalog')

    for brain in catalog(object_provides=interfaceToName(context, iface)):
        obj = brain.getObject()
        if iface in interface.directlyProvidedBy(obj):
            yield brain.getObject()

def persist_five_components(context, product_name):
    """Make sure QI doesn't uninstall the Five-created utilities folder
    in a plone site.

      >>> class Mock(object):
      ...     def __init__(self, **kwargs):
      ...         for key, val in kwargs.items(): setattr(self, key, val)
      ...     def __getitem__(self, key): return self.__dict__[key]

      >>> qi = Mock()
      >>> portal = Mock(portal_quickinstaller=qi)
      >>> context = Mock(portal_url=Mock(getPortalObject=lambda: portal))

    At first SomeProduct isn't actually installed so we get a KeyError.

      >>> persist_five_components(context, 'SomeProduct')
      Traceback (most recent call last):
      KeyError: 'No product installed with the name "SomeProduct"'

      >>> qi.SomeProduct = Mock(portalobjects=['abc', 'def'])
      >>> persist_five_components(context, 'SomeProduct')
      >>> qi.SomeProduct.portalobjects
      ['abc', 'def']

      >>> qi.SomeProduct.portalobjects.append('utilities')
      >>> qi.SomeProduct.portalobjects
      ['abc', 'def', 'utilities']

      >>> persist_five_components(context, 'SomeProduct')
      >>> qi.SomeProduct.portalobjects
      ['abc', 'def']

    """

    portal_url = cmfutils.getToolByName(Acquisition.aq_inner(context),
                                        'portal_url')
    portal = portal_url.getPortalObject()
    qi = portal.portal_quickinstaller
    try:
        ip = qi[product_name]
    except KeyError, e:
        raise KeyError('No product installed with the name "%s"' %
                       str(product_name))

    if 'utilities' in getattr(ip, 'portalobjects', []):
        portalobjects = [x for x in ip.portalobjects
                         if x != 'utilities']
        ip.portalobjects = portalobjects
