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
## Script (Python) "livescript_reply"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=q,limit=10,path=None
##title=Determine whether to show an id in an edit form

from Products.CMFCore.utils import getToolByName
from ubify.cyninv2theme import getCyninMessageFactory
from Products.CMFPlone.browser.navtree import getNavigationRoot
from Products.CMFPlone.utils import safe_unicode
from Products.PythonScripts.standard import url_quote
from Products.PythonScripts.standard import url_quote_plus
from Products.PythonScripts.standard import html_quote

_ = getCyninMessageFactory()

ploneUtils = getToolByName(context, 'plone_utils')
portal_url = getToolByName(context, 'portal_url')()
pretty_title_or_id = ploneUtils.pretty_title_or_id
plone_view = context.restrictedTraverse('@@plone')

portalProperties = getToolByName(context, 'portal_properties')
siteProperties = getattr(portalProperties, 'site_properties', None)
useViewAction = []
if siteProperties is not None:
    useViewAction = siteProperties.getProperty('typesUseViewActionInListings', [])

# SIMPLE CONFIGURATION
USE_ICON = True
USE_RANKING = False
MAX_TITLE = 29
MAX_DESCRIPTION = 93

# generate a result set for the query
catalog = context.portal_catalog

friendly_types = ploneUtils.getUserFriendlyTypes()

def quotestring(s):
    return '"%s"' % s

def quote_bad_chars(s):
    bad_chars = ["(", ")"]
    for char in bad_chars:
        s = s.replace(char, quotestring(char))
    return s

# for now we just do a full search to prove a point, this is not the
# way to do this in the future, we'd use a in-memory probability based
# result set.
# convert queries to zctextindex

# XXX really if it contains + * ? or -
# it will not be right since the catalog ignores all non-word
# characters equally like
# so we don't even attept to make that right.
# But we strip these and these so that the catalog does
# not interpret them as metachars
##q = re.compile(r'[\*\?\-\+]+').sub(' ', q)
for char in '?-+*':
    q = q.replace(char, ' ')
r=q.split()
r = " AND ".join(r)
r = quote_bad_chars(r)+'*'
searchterms = url_quote_plus(r)

site_encoding = context.plone_utils.getSiteEncoding()
if path is None:
    path = getNavigationRoot(context)
results = catalog(SearchableText=r, portal_type=friendly_types, path=path)

searchterm_query = '?searchterm=%s'%url_quote_plus(q)

RESPONSE = context.REQUEST.RESPONSE
RESPONSE.setHeader('Content-Type', 'text/xml;charset=%s' % site_encoding)

# replace named entities with their numbered counterparts, in the xml the named ones are not correct
#   &darr;      --> &#8595;
#   &hellip;    --> &#8230;
legend_livesearch = _('legend_livesearch', default='LiveSearch &#8595;')
label_no_results_found = _('label_no_results_found', default='No matching results found.')
label_advanced_search = _('label_advanced_search', default='Advanced Search&#8230;')
label_show_all = _('label_show_all', default='Show all&#8230;')

ts = getToolByName(context, 'translation_service')

output = []

def write(s):
    output.append(safe_unicode(s))


if not results:
    write('''<fieldset class="livesearchContainer">''')
    write('''<div id="livesearchLegend">%s</div>''' % ts.translate(legend_livesearch))
    write('''<div class="LSIEFix">''')
    write('''<div id="LSNothingFound">%s</div>''' % ts.translate(label_no_results_found))
    write('''<div class="LSRow">''')
    write('<a href="search_form" style="font-weight:normal">%s</a>' % ts.translate(label_advanced_search))
    write('''</div>''')
    write('''</div>''')
    write('''</fieldset>''')

else:
    write('''<fieldset class="livesearchContainer">''')
    write('''<div id="livesearchLegend">%s</div>''' % ts.translate(legend_livesearch))
    write('''<div class="LSIEFix">''')
    write('''<ul class="LSTable">''')
    for result in results[:limit]:

        icon = plone_view.getIcon(result)
        itemUrl = result.getURL()
        if result.portal_type in useViewAction:
            itemUrl += '/view'
        full_title = safe_unicode(pretty_title_or_id(result))
        if result.portal_type == 'Discussion Item':
            itemUrl = itemUrl.replace('/talkback/' + result.getId, '/view')
            itemUrl = itemUrl + searchterm_query + '#' + result.getId
            full_title = safe_unicode(result.getObject().text)
        else:
            itemUrl = itemUrl + searchterm_query

        write('''<li class="LSRow">''')
        
        if len(full_title) > MAX_TITLE:
            display_title = ''.join((full_title[:MAX_TITLE],'...'))
        else:
            display_title = full_title
        full_title = full_title.replace('"', '&quot;')
        write('''<a href="%s" title="%s">''' % (itemUrl, full_title))
        if icon.url is not None and icon.description is not None:
            write('''<img src="%s" alt="%s" width="%i" height="%i" />''' % (icon.url,
                                                                            icon.description,
                                                                            icon.width,
                                                                            icon.height))
        write('''%s''' % display_title)
        write('''<span class="discreet">[%s%%]</span>''' % result.data_record_normalized_score_)
        display_description = safe_unicode(result.Description)
        if len(display_description) > MAX_DESCRIPTION:
            display_description = ''.join((display_description[:MAX_DESCRIPTION],'...'))
        # need to quote it, to avoid injection of html containing javascript and other evil stuff
        display_description = html_quote(display_description)
        write('''<div class="discreet" style="margin-left: 2.5em;">%s</div></a>''' % (display_description))
        write('''</li>''')
        full_title, display_title, display_description = None, None, None

    write('''<li class="LSRow">''')
    write( '<a href="search_form" style="font-weight:normal">%s</a>' % ts.translate(label_advanced_search))
    write('''</li>''')

    if len(results)>limit:
        # add a more... row
        write('''<li class="LSRow">''')
        write( '<a href="%s" style="font-weight:normal">%s</a>' % ('search?SearchableText=' + searchterms, ts.translate(label_show_all)))
        write('''</li>''')
    write('''</ul>''')
    write('''</div>''')
    write('''</fieldset>''')

return '\n'.join(output).encode(site_encoding)
