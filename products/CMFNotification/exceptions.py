"""Define CMFNotification specific exceptions.

$Id: exceptions.py 33881 2006-11-18 15:42:29Z dbaty $
"""

class MailHostNotFound(Exception):
    """Could not send notification: no mailhost found"""

class DisabledFeature(Exception):
    """Cannot use this feature: it is disabled"""

class InvalidEmailAddress(Exception):
    """The given email address is not valid"""
