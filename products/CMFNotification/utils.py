"""Utility methods for CMFNotification.

$Id: utils.py 67788 2008-07-04 08:16:40Z dbaty $
"""

import re
from email.Header import Header

from AccessControl import getSecurityManager
from Products.PageTemplates.Expressions import getEngine
from Products.PageTemplates.Expressions import SecureModuleImporter

from Products.CMFCore.utils import getToolByName
from Products.CMFCore.WorkflowCore import WorkflowException


EMAIL_ADDRESS_IN_HEADER_REGEXP = re.compile('(?:\s*,\s*)?(.*?) <(.*?)>')


def getBasicBindings(obj):
    """Return basic bindings to build expression context and provide
    options to ZPT mail templates.
    """
    mtool = getToolByName(obj, 'portal_membership')
    wtool = getToolByName(obj, 'portal_workflow')
    try:
        current_state = wtool.getInfoFor(obj, 'review_state')
    except WorkflowException:
        current_state = None

    return {
        'current_state': current_state,
        'author': mtool.getAuthenticatedMember(),
        }


def getExpressionContext(obj, extra_bindings=None):
    """An expression context provides names for TALES expressions.

    Based on ``DCWorkflow.Expression`` and ``CMFCore.Expression``. We
    add ``getBasicBindings()`` and then ``extra_bindings`` if is it
    provided.
    """
    portal = getToolByName(obj, 'portal_url').getPortalObject()

    data = {
        'here': obj,
        'context': obj,
        'nothing': None,
        'portal': portal,
        'request': getattr(obj, 'REQUEST', None),
        'modules': SecureModuleImporter,
        }
    data.update(getBasicBindings(obj))

    if extra_bindings is not None:
        data.update(extra_bindings)

    return getEngine().getContext(data)


def encodeMailHeaders(message, encoding):
    """Return ``message`` with correctly encoded headers.

    The following headers are encoded: ``From``, ``Reply-to``,
    ``Sender``, ``Cc`` and ``Subject``.
    """
    mout = []
    lines = message.split('\n')
    for line_i in range(0, len(lines)):
        line = lines[line_i]
        if not line:
            break ## End of headers block.
        header = line[:line.find(':')]
        if header.lower() in ('from', 'reply-to', 'sender',
                              'cc', 'subject'):
            value = line[len(header) + 1:].lstrip()
            if header.lower() in ('from', 'reply-to', 'sender', 'cc'):
                ## We must not encode e-mail addresses.
                addresses = EMAIL_ADDRESS_IN_HEADER_REGEXP.findall(value)
                if addresses:
                    addresses = [(Header(s, encoding).encode(), addr) \
                                 for s, addr in addresses]
                    value = ', '.join(['%s <%s>' % (s, addr) \
                                       for (s, addr) in addresses])
            else:
                value = Header(value, encoding).encode()
            mout.append('%s: %s' % (header, value))
            continue
        mout.append(line)
    mout.extend(lines[line_i:])
    return '\n'.join(mout)


def getPreviousWorkflowState(obj):
    """Return previous workflow state of ``obj`` or ``None`` if no
    previous state exists.
    """
    ## We suppose that there is only one workflow.
    history = obj.workflow_history.values()[0]
    if len(history) <= 1:
        return None
    return history[-2]['review_state']


def getPreviousVersion(obj):
    """Return previous version of the object, or ``None`` if none
    could be found or if the current user is not authorized to
    retrieve it.
    """
    rtool = getToolByName(obj, 'portal_repository')
    try:
        history = rtool.getHistory(obj)
    except Unauthorized:
        return None
    if not history:
        return None
    return history[0].object

def removeActionInitiatorFromUsers(users,author):
    userid = author.getUser().getId()
    if users.__contains__(userid):
        users.remove(userid)
    return users
