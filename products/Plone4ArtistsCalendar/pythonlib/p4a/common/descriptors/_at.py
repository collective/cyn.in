
class ATSchemaFieldDescriptor(property):
    """A descriptor for accessing AT schema fields.

      >>> class Mock(object):
      ...     def __init__(self, **kwargs):
      ...         for key, value in kwargs.items(): setattr(self, key, value)
      >>> class MockField(object):
      ...     def __init__(self, v=''): self.attr = v
      ...     def getAccessor(self, x):
      ...         return lambda obj=self: obj.attr
      ...     def getMutator(self, x):
      ...         def set(v, obj=self):
      ...             obj.attr = v
      ...         return set
      >>> mockfield = MockField()
      >>> someattr = Mock(schema={'foobar': mockfield})
      >>> class MockTest(object):
      ...     someattr = someattr
      ...     somefield = ATSchemaFieldDescriptor('foobar', 'someattr')
      >>> obj = MockTest()

      >>> obj.somefield
      u''

      >>> obj.somefield = 'abc'
      >>> obj.somefield
      u'abc'

      >>> obj.somefield = u'someuni'
      >>> obj.somefield
      u'someuni'

    """

    def __init__(self, field, subobj_name=None, uni=True):
        self.field = field
        self.subobj_name = subobj_name
        self.ensure_unicode = uni

    def _decode(self, v):
        v = v or u''
        if not isinstance(v, unicode) and self.ensure_unicode:
            v = unicode(v, 'utf-8')
        return v

    def obj(self, obj):
        if self.subobj_name:
            obj = getattr(obj, self.subobj_name)
        return obj

    def atfield_accessor(self, obj):
        obj = self.obj(obj)
        return obj.schema[self.field].getAccessor(obj)

    def atfield_mutator(self, obj):
        obj = self.obj(obj)
        return obj.schema[self.field].getMutator(obj)

    def __get__(self, obj, type=None):
        return self._decode(self.atfield_accessor(obj)())

    def __set__(self, obj, v):
        self.atfield_mutator(obj)(self._decode(v))

    def __delete__(self, obj):
        self.atfield_mutator(obj)(None)
