## Copyright (c) 2007-2008 Damien Baty
##
## This file is free software; you can redistribute it and/or modify
## it under the terms of the GNU General Public License as published
## by the Free Software Foundation; either version 3 of the License,
## or (at your option) any later version.
##
## This file is distributed in the hope that it will be useful, but
## WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
## General Public License for more details.
##
## You should have received a copy of the GNU General Public License
## along with this program.  If not, see
## <http://www.gnu.org/licenses/>.

"""Define ``FakeLogger`` and ``FakeRootLogger`` classes, which can be
used to monkey-patch the corresponding classes of the ``logging``
package so that every messages is stored in the logger itself and can
then be checked against what was expected to be logged.

Basic usage
===========

Suppose that we want to test this method::

    >>> import logging
    >>> def foo():
    ...     ## Do things
    ...     logging.warning("OMG, we've done horrible things!")

We can probably test that things have been done, but we may also want
to check that the warning has been logged, too. To do that, we first
call the ``patch`` method::

    >>> from fakelogger import patchLogging
    >>> patchLogging()

Now we have a fake logger, which do not actually write anything to a
file or to the standard error. It has additional methods with which we
can test that our method has actually logged what we expected it to::

    >>> foo()
    >>> from logging import getLogger
    >>> logger = getLogger()
    >>> logger.getStack()
    ["OMG, we've done horrible things!"]

Obviously, as the name of the method suggests, the logger has a
stack. So if we call our method again, we will have the warning
twice::

    >>> foo()
    >>> logger.getStack()
    ["OMG, we've done horrible things!", "OMG, we've done horrible things!"]

That can be quite handy if we have to log multiple things in an
integration test, for example. However, for unit tests, it is often
useful to clear the stack::

    >>> logger.clearStack()
    >>> logger.getStack()
    []

That is why the "natural" usage could be::

    >>> logger.clearStack() ## You never know...
    >>> foo()
    >>> logger.getStack() ## The test itself
    ["OMG, we've done horrible things!"]
    >>> logger.clearStack() ## Be kind to other test(er)s

Note that in the previous example, we have used the root logger by
using ``getLogger`` without any parameter. We can use any logger,
though::

    >>> logger = getLogger('My own logger')
    >>> def bar():
    ...     ## Do other horrible things
    ...     logger.error('We have killed Kenny.')
    >>> bar()
    >>> logger.getStack()
    ['We have killed Kenny.']


Advanced usage
==============

There is no advanced usage, yet. See FIXME below.


$Id: fakelogger.py 55153 2007-12-09 12:42:44Z dbaty $
"""

## FIXME: could we not use 'MemoryHandler'?

import logging
from logging import Logger
from logging import RootLogger
from logging import WARNING


def patchLogging():
    logging._loggerClass = FakeLogger
    logging.root = FakeRootLogger(WARNING)


class FakeLogger(Logger):
    def _log(self, level, msg, args, exc_info=None):
        """Store ``msg`` in a stack."""
        stack = self.getStack()
        stack.append(msg % args)
        ## FIXME: this is a bit basic, for now:
        ## - what if exc_info is True?
        ## - do we want to check log records level (severity)?


    def getStack(self):
        if not hasattr(self, '_stack'):
            self.clearStack()
        return self._stack


    def clearStack(self):
        self._stack = []


class FakeRootLogger(FakeLogger, RootLogger):
    pass



def _test():
    import doctest
    doctest.testmod()

if __name__ == "__main__":
    _test()
