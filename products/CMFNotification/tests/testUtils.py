"""Test pure Python functions of CMFNotification ``utils`` module.

$Id: testUtils.py 67788 2008-07-04 08:16:40Z dbaty $
"""

from unittest import TestCase

from Products.CMFNotification.utils import encodeMailHeaders


MSG1 = '''\
From: george@example.com
Sender: George <george@example.com>
To: eric@example.com
Subject: My guitar gently weeps

Eric, my guitar weeps. Gently, sure, but it weeps. What shall I do?
'''

MSG1_ENCODED = '''\
From: george@example.com
Sender: =?utf-8?q?George?= <george@example.com>
To: eric@example.com
Subject: =?utf-8?q?My_guitar_gently_weeps?=

Eric, my guitar weeps. Gently, sure, but it weeps. What shall I do?
'''

MSG2 = '''\
From: Andrew <andrew@example.com>, Dick <dick@example.com>
Sender: Andrew <andrew@example.com>
Reply-To: Andrew <andrew@example.com>
CC: Jim <jim@example.com>
Subject: What happened to the door?

What happened to the door?! It was red, and now it's black. This is
not funny. And Jim, get off that snake, immediately!
'''

MSG2_ENCODED = '''\
From: =?utf-8?q?Andrew?= <andrew@example.com>, =?utf-8?q?Dick?= <dick@example.com>
Sender: =?utf-8?q?Andrew?= <andrew@example.com>
Reply-To: =?utf-8?q?Andrew?= <andrew@example.com>
CC: =?utf-8?q?Jim?= <jim@example.com>
Subject: =?utf-8?q?What_happened_to_the_door=3F?=

What happened to the door?! It was red, and now it's black. This is
not funny. And Jim, get off that snake, immediately!
'''

MESSAGES = ((MSG1, MSG1_ENCODED),
            (MSG2, MSG2_ENCODED),
            )


class TestEncodeMailHeaders(TestCase):
    """Various tests for ``utils.encodeMailHeaders()``."""

    def testEncoding(self):
        for raw, expected in MESSAGES:
            encoded = encodeMailHeaders(raw, 'utf-8')
            self.failUnlessEqual(encoded, expected)

def test_suite():
    import unittest
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestEncodeMailHeaders))
    return suite
