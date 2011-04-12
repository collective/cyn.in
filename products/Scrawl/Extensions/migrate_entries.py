"""To use, ensure that the contentmigrations product is available
   in your products directory, then add an external method to the 
   portal_skins/custom directory (in the ZMI) such that:
   
   id = migrateQuills
   title = migrateQuills
   module name = Scrawl.migrate_entries
   function name = migrate

   To migrate Quills weblog entries to Scrawl blog entries, simply click
   the 'test' tab. Weblog entries are converted in place to blog entries.
   Cutting and pasting the newly-created blog entries will fix the obvious
   workflow and title weirdness. (You do have a back-up, don't you?)

   For more information on content type migration, see:
   http://plone.org/documentation/tutorial/richdocument/migrations
   
   Migration by Trey Beck
"""


from Products.CMFCore.utils import getToolByName
from StringIO import StringIO
from Products.contentmigration.basemigrator.walker import CatalogWalker
from Products.contentmigration.basemigrator.migrator import CMFItemMigrator

class WeblogEntryMigrator(CMFItemMigrator):

    walkerClass = CatalogWalker
    src_meta_type = 'WeblogEntry'
    src_portal_type = 'WeblogEntry'
    dst_meta_type = 'News Item'
    dst_portal_type = 'Blog Entry'
    map = {'getRawText' : 'setText'}

def migrate(self):
    """Run the migration"""

    out = StringIO()
    print >> out, "Starting migration"

    portal_url = getToolByName(self, 'portal_url')
    portal = portal_url.getPortalObject()
    cat = getToolByName(self, 'portal_catalog')

    migrators = (WeblogEntryMigrator,)

    for migrator in migrators:
        walker = migrator.walkerClass(portal, migrator)
        walker.go(out=out)
        print >> out, walker.getOutput()
    # update the portal_type
    results=cat(portal_type=migrator.dst_portal_type)
        for brain in results:
            ob = brain.getObject()
            ob._setPortalTypeName(migrator.dst_portal_type)
            ob.reindexObject(['portal_type'])
    
    # And let's also update workflows
    #print >> out, "Updating workflow"
    #wf = getToolByName(self, 'portal_workflow')
    #wf.updateRoleMappings()

    # Update Kupu settings
    #print >> out, "Applying Kupu customizations"
    #for type in linkableKupuTypes:
    #    self.addKupuResource('linkable', type)
    #for type in mediaKupuTypes:
    #    self.addKupuResource('mediaobject', type)        
    #for type in collectionKupuTypes:
    #    self.addKupuResource('collection', type)
    
    print >> out, "Migration finished"
    return out.getvalue()
