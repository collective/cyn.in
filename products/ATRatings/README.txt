ATRatings is a tool for storing user ratings and hits on objects for Archetypes
based content.

ATRatings uses a pluggable storage mechanism for rating data.  So far I have
written a ZODB-based storage that strives to be reasonably efficient with 
memory.

ATRatings makes use of references and hence requires Archetypes.  It indexes
stored ratings using object UIDs, so until UIDs are backported into the CMF,
you can only rate Archetypes-based objects.

NOTE: This products works for Archetypes based content only. So it is a product
for Plone 2.1 which is based on ATContentTypes.

For the API methods, see API.txt.

How to use it?
----------------------------
1. Enable ratings and click counting

   ATRatings disabled such functions by default. You should go to ZMI inface of 
   the folder where you want to enable them. Click the Properties tab, and add 2
   boolean properties:

   - enableRatings : enable ratings for contents in the folder
   - enableCountings : enable click countings for content in the folder

2. put following macro 'here/rating_macros/macros/portlet' to your template. 
   for example, add it to document_byline.pt or the left_slots propertis in ZMI.

3. Simple rating statistics.

   Add 2 portlets in your left_slots or right_slots::

      here/portlet_top_ratings/macros/portlet
      here/portlet_top_countings/macros/portlet

   You can also use similar viewlets with CMFContentPanels if you intalled.

4. You can control who can vote by permission: "ATRatings: Add rating".

5. You can control which content types are enabled by 2 protal_ratings properties:
   'allowed_rating_types' and 'allowed_couting_types'.


When uninstalling:
----------------------------
ATRatings product uses references to keep ratings for portal content in ratings
tool. These are unwanted for example if you want to export some of the content
and import it to other Plone portal without ATRatings installed.

In this case set option CLEAR_REFS_ON_UNINSTALL=1 in config.py module to remove
these references during product uninstallation.