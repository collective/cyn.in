import os
import sys
from App import Common as appcommon
from Products.Five import zcml

def setup_basedir_pythonpath(basedir):
    """Ensure all directories beneath *basedir* are setup on the
    python path.
    """

    valid = [d for d in os.listdir(basedir) if not d.startswith('.') and \
               os.path.isdir(os.path.join(basedir, d))]

    for entry in valid:
        full = os.path.join(basedir, entry)
        setup_pythonpath(full, entry)

    return valid

def setup_pythonpath(full, package):
    """Add the given directory to the pythonpath and fix any existing
    __path__ entries belonging to *package* if possible to accomodate 
    namespace packages.
    """
    
    if full not in sys.path:
        sys.path.append(full)
        
        last = ''
        for x in package.split('.'):
            v = last
            if v:
                v += '.'
            v += x
            
            # if the module has already been loaded and is being
            # pulled from somewhere else, we need to add it here
            if sys.modules.has_key(v):
                f = os.path.join(full, '/'.join(v.split('.')))
                m = sys.modules[v]
                if f not in m.__path__:
                    m.__path__.append(f)
            last = v

def load_extrazcml(items):
    """Load all of the configure.zcml's for the given packages.
    """

    for entry in items:
        m = __import__(entry, {}, {}, entry)
        
        try:
            zcml.load_config('configure.zcml', m)
        except IOError: # No file
            pass

class InitBuilder(object):
    """InitBuilder is simply a helper for constructing the ``__init__.py``
    for a Zope 2 product that adds all extralibs based python packages
    to the pythonpath and loads their zcml.

      >>> builder = InitBuilder(globals=globals())
      >>> builder.setup_pythonpath()
      []
      
      >>> builder.init_gen()
      <function initialize ...>
      
    """
    
    def __init__(self, package=None, globals=None, extralibs='extralibs'):
        if package is None and globals is None:
            raise ValueError('Either package or globals must be specified')
        
        self.package = package or globals['__name__']
        self.extralibs = extralibs

    def setup_pythonpath(self):
        pkg_home = appcommon.package_home({'__name__': self.package})
        basedir = os.path.join(pkg_home, self.extralibs)
        if not os.path.isdir(basedir):
            return []
        
        self.extralibs_configured = \
            [os.path.basename(x) 
             for x in setup_basedir_pythonpath(basedir)]
            
        return self.extralibs_configured

    def init_gen(self):
        def initialize(context):
            load_extrazcml(['p4a.common']) # needs to be loaded first
            load_extrazcml(self.extralibs_configured)

        return initialize
