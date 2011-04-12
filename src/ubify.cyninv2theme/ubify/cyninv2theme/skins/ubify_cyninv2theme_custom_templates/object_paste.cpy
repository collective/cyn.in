###############################################################################
##cyn.in is an open source Collaborative Knowledge Management Appliance that 
##enables teams to seamlessly work together on files, documents and content in 
##a secure central environment.
##
##cyn.in v2 an open source appliance is distributed under the GPL v3 license 
##along with commercial support options.
##
##cyn.in is a Cynapse Invention.
##
##Copyright (C) 2008 Cynapse India Pvt. Ltd.
##
##This program is free software: you can redistribute it and/or modify it under
##the terms of the GNU General Public License as published by the Free Software 
##Foundation, either version 3 of the License, or any later version and observe 
##the Additional Terms applicable to this program and must display appropriate 
##legal notices. In accordance with Section 7(b) of the GNU General Public 
##License version 3, these Appropriate Legal Notices must retain the display of 
##the "Powered by cyn.in" AND "A Cynapse Invention" logos. You should have 
##received a copy of the detailed Additional Terms License with this program.
##
##This program is distributed in the hope that it will be useful,
##but WITHOUT ANY WARRANTY; without even the implied warranty of 
##MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General 
##Public License for more details.
##
##You should have received a copy of the GNU General Public License along with 
##this program.  If not, see <http://www.gnu.org/licenses/>.
##
##You can contact Cynapse at support@cynapse.com with any problems with cyn.in. 
##For any queries regarding the licensing, please send your mails to 
## legal@cynapse.com
##
##You can also contact Cynapse at:
##802, Building No. 1,
##Dheeraj Sagar, Malad(W)
##Mumbai-400064, India
###############################################################################
## Controller Python Script "object_paste"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind state=state
##bind subpath=traverse_subpath
##parameters=
##title=Paste objects into the parent/this folder
##

from Products.CMFPlone.utils import transaction_note
from Products.CMFPlone import PloneMessageFactory as _
from AccessControl import Unauthorized
from ZODB.POSException import ConflictError
from ubify.cyninv2theme import validatePasteData,PasteError

msg=_(u'Copy or cut one or more items to paste.')

if context.cb_dataValid:
    try:
        validatePasteData(context,context.REQUEST['__cp'])
        context.manage_pasteObjects(context.REQUEST['__cp'])        
        transaction_note('Pasted content to %s' % (context.absolute_url()))
        context.plone_utils.addPortalMessage(_(u'Item(s) pasted.'))
        return state
    except PasteError,e:
        msg= e
    except ConflictError:
        raise
    except ValueError:
        msg=_(u'Disallowed to paste item(s).')
    except (Unauthorized, 'Unauthorized'):
        msg=_(u'Unauthorized to paste item(s).')
    except: # fallback
        msg=_(u'Paste could not find clipboard content.')

context.plone_utils.addPortalMessage(msg, 'error')
return state.set(status='failure')
