import os

def package_dirs(pkg_name):
    """Return the physical filesystem directory (if possible) of the given
    package.

      >>> package_dirs('p4a.common')
      ('...p4a/common',)

    Feeding a module name will result in returning the paths of the parent
    package.

      >>> package_dirs('p4a.common.pkgutils')
      ('...p4a/common',)

    Feeding a non-existent package/module will simply raise an ImportError.

      >>> package_dirs('p4a.common.foobar')
      Traceback (most recent call last):
        ...
      ImportError: No module named foobar

    """

    pkg = __import__(pkg_name, globals(), locals(), pkg_name)
    if not hasattr(pkg, '__path__'):
        # pkg_name was actually the name of a module, lets get the actual pkg
        pkg_name = '.'.join(pkg_name.split('.')[:-1])
        pkg = __import__(pkg_name, globals(), locals(), pkg_name)

    return tuple(getattr(pkg, '__path__', ()))

def find_dir(pkg_name, dirname='.'):
    """Return an absolute path to a directory if one can be found, or None
    otherwise.  The search is recursive starting at the directories
    provided by pkg_name.

      >>> find_dir('p4a.common', '.')
      '.../p4a/common'

    The search will be recursive, in this example it will look at all pkg dirs
    provided by 'p4a' and recursively search for pkgutils.py.

      >>> find_dir('p4a', 'pkgutils.py')
      '.../p4a/common/pkgutils.py'
    """

    # special case, basically means return the first directory provided by
    # the package
    if dirname == '.':
        dirs = package_dirs(pkg_name)
        if len(dirs) > 0:
            return dirs[0]
        return None

    def find(basedir, dirname=dirname):
        for x in os.listdir(basedir):
            full = os.path.join(basedir, x)
            if x == dirname:
                return full
            elif os.path.isdir(full):
                res = find(full)
                if res:
                    return res

    for x in package_dirs(pkg_name):
        res = find(x)
        if res:
             return res

    return None
