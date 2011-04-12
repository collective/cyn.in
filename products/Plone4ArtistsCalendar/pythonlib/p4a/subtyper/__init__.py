from zope import component
from p4a.subtyper.interfaces import ISubtyper

from Products.CMFCore import DirectoryView
DirectoryView.registerDirectory('skins', globals())

class activated(property):
    """A descriptor for setting or getting whether a subtype
    has been applied to an object.
    """

    def __init__(self, desc_name, attr=None):
        self.desc_name = desc_name
        self.attr = attr

    def get_obj(self, obj):
        if not self.attr:
            return obj
        return getattr(obj, self.attr, None)

    def __get__(self, obj, type=None):
        subtyper = component.queryUtility(ISubtyper)
        if subtyper is None:
            return False
        realobj = self.get_obj(obj)
        if realobj is None:
            return False

        descwithname = subtyper.existing_type(realobj)
        if descwithname is None:
            return False
        return descwithname.name == self.desc_name

    def __set__(self, obj, v):
        subtyper = component.getUtility(ISubtyper)
        v = bool(v)
        orig = self.__get__(obj)
        realobj = self.get_obj(obj)
        if v and not orig:
            subtyper.change_type(realobj, self.desc_name)
        elif not v and orig:
            subtyper.remove_type(realobj)

    def __delete__(self, obj):
        self.__set__(obj, False)
