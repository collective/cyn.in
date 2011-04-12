import os.path
from Globals import package_home

wwwDirectory = os.path.join(package_home(globals()), 'www')

def _firstIdAndInstanceOfClass(container, class_):
    """Return the ID and instance of the first object of class `class_` within `container`. If there is none, return (None, None)."""
    for id in container.objectIds():
        if isinstance(container[id], class_):
            return id, container[id]
    return None, None

def firstIdOfClass(container, class_):
    """Return the ID of the first object of class `class_` within `container`. If there is none, return None."""
    return _firstIdAndInstanceOfClass(container, class_)[0]

def firstInstanceOfClass(container, class_):
    """Return the first object of class `class_` within `container`. If there is none, return None."""
    return _firstIdAndInstanceOfClass(container, class_)[1]
