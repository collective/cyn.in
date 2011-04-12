Description

    Scrawl is a dirt-simple blog product for Plone.  It copies the "News Item"
    content type to create a "Blog Entry" (with a slightly tweaked view template)
    and adds an alternative view to Smart Folders (blog_view).  Note that blog_view
    shows either the description of each contained blog entry (if it exists) or the
    entire body in it, so it's up to the user to limit those results in an intelligent
    way so that page loads doesn't take too long.
    
    Scrawl works in Plone 2.1, 2.5, and 3.0.

Installation

    Place Scrawl in the Products directory of your Zope instance
    and restart the server.  Either go to the 'Site Setup' page in Plone
    and click on 'Add/Remove Products' or use the Quick Installer in the ZMI.

Migration
    There is a basic migrator available for Quills -> Scrawl.  Read the docstring in Products.Scrawl.Extensions.migrate_entries for more details.  YMMV.

Written by

    ONE/Northwest <jonb@onenw.org>
