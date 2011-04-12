Plone4ArtistsCalendar
=====================

Overview
--------

Plone4ArtistsCalendar is a Plone product built to expose the
``p4a.plonecalendar`` framework in a Plone setting.  In a nutshell it provides
the following features:

Calendar support
  Any folder or smart folder can be *calendar activated* which turns it into
  a calendar which knows how to display an overview for all contained events.

Monthly view
  Any calendar activated (smart) folder can has several default views
  including a monthly view.

Chronological event view
  The events gathered together by the activated calendar can be displayed
  using a chronological event listing.
  
Past events view
  Events that have already occurred are grouped into a past events listing page.

Color coding by event type
  Events can be color coded based on what event type (keyword) they have 
  been assigned.
  
iCal and hCal support
  Exporting events in iCal format and importing iCal and hCal. Publishing a calendar from Apple iCal or Mozilla Sunbird to your Plone site.


Requirements
------------

- Zope 2.9.8+  or Zope 2.10+
- Plone 2.5.3+  or Plone 3.0+
- Five_ 1.4.3+ (if running Zope 2.9.8) or Five 1.5+ (Included in Zope 2.10)
- Calendaring 0.4.0+
- Marshall SVN trunk r7066 or higher

.. _Five: http://codespeak.net/z3/five/

Installation
------------

If you're installing from the *Plone4ArtistsCalendar* bundle release you
simply need to install all of the included Zope2 products into your
``$INSTANCE_HOME/Products`` directory.

If you're installing just the *Plone4ArtistsCalendar* Zope 2 product,
you'll need the other dependencies installed manually as well.  Please
see their install files for proper installation instructions.

Configuration within a Plone site is simply a matter of going to the
*Add/Remove Products* configlet and installing the ``Plone4ArtistsCalendar``
product.

Basic Usage
-----------

Note: The Plone4ArtistsCalendar product does not install any content types.

- folders and smart folders can be toggled to be calendar enhanced
  (become calendars) by selecting the **configure calendar** menu item in
  their respective **actions** drop down menu's.

Directory Layout
----------------

Please note that this product is just a Zope 2 integration layer for the
``p4a.calendar`` and ``p4a.plonecalendar`` python packages.  See the actual
python package directories within the
``$INSTANCE_HOME/Products/Plone4ArtistsCalendar/pythonlib`` directory for
further details.

Testing
-------

To run the Plone4ArtistsCalendar tests you must use the standard Zope
testrunner::

    $INSTANCE_HOME/bin/zopectl test -m Products.Plone4ArtistsCalendar.tests

Running the tests any other way (such as with the -s option) will result
in the testrunner finding unrunnable tests due to *PYTHONPATH* mangling.
