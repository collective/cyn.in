from zope import schema
from StringIO import StringIO
from zipfile import ZipFile, BadZipfile
from zope.schema._bootstrapinterfaces import WrongType

class ZipFileLine(schema.TextLine):

    def _validate(self, value):
        """ Overwrites validator for FileWidget  """
        try:
            ZipFile(StringIO(value))
        except BadZipfile, e:
            raise WrongType(e)


