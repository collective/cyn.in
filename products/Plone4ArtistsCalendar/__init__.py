import os
import sys

try:
    pythonlib = os.path.join(os.path.dirname(__file__), 'pythonlib')
    sys.path.append(pythonlib)
except NameError, e:
    pass
