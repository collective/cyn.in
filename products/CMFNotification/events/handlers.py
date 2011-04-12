"""Event handlers for CMFNotification.

See ``events.txt`` for further details.

$Id: handlers.py 67204 2008-06-24 06:09:50Z dbaty $
"""

from Products.CMFCore.utils import getToolByName

from Products.CMFNotification.NotificationTool import ID


def onObjectInitializedEvent(obj, event):
    """Subscriber for ``ObjectInitializeEvent``."""
    ntool = getToolByName(obj, ID, None)
    if ntool is not None:
        ntool.onItemCreation(obj)


def onObjectClonedEvent(obj, event):
    """Subscriber for ``ObjectClonedEvent``."""
    ntool = getToolByName(obj, ID, None)
    if ntool is not None:
        ntool.onItemCreation(obj)


def onObjectEditedEvent(obj, event):
    """Subscriber for ``ObjectModifiedEvent``."""
    ntool = getToolByName(obj, ID, None)
    if ntool is not None:
        ntool.onItemModification(obj)


def onActionSucceededEvent(obj, event):
    """Subscriber for ``ActionSucceededEvent``."""
    ntool = getToolByName(obj, ID, None)
    if ntool is not None:
        ntool.onWorkflowTransition(obj, event.action)


def onDiscussionItemAddedEvent(obj, event):
    """Subscriber for ``ObjectAddedEvent`` on discussion items."""
    ntool = getToolByName(obj, ID, None)
    if ntool is not None:
        ntool.onDiscussionItemCreation(obj)
