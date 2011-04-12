.. -*- coding: utf-8 -*-

===============
CMFNotification
===============

CMFNotification is a Plone product that allows users to be notified
when various events occur in the portal:

- when an item is created or copy-pasted;

- when an item is modified;

- when a workflow transition occurs.

Other notifications might be implemented but, for now, only the three
above can be safely used. (In other words, do not trust the
configuration form, which includes for example fields for discussion
notification, although it is **not** implemented.)

CMFNotification is configured with rules:

- rules to decide who should be notified;

- rules to decide what mail template to use.

Besides these rules, CMFNotification handles extra subscription to any
portal item. This allows authenticated users to subscribe to an item
and receive notification, if the notification policy does not already
include him/her in the list of notified users. These extra
subscription may be recursive: if so, an user which has subscribed to
a folder is notified for any event which occurs on the folder and any
of its items (including its subfolders, etc.).


Dependencies
============

This version of CMFNotification has the following dependencies:

- Zope 2.10.x ;

- Plone 3.x.

Despite the name, this product may not work in a pure CMF
portal. Minor changes may be needed. I thought about having an
implementation which works for pure CMF portals, hence the
name. However, use-cases rules and I did not have any pure CMF
use-case... This may or may not happen in the future.

**Important note:** please note that the standard Secure MailHost
(which is shipped with Plone) and its base product (MailHost) are not
intended to send a lot of emails. It is highly suggested to install
`MaildropHost`_ if you are about to do so.

.. _MaildropHost: http://www.dataflake.org/software/maildrophost


Installation and configuration
==============================

See ``doc/install.txt``.


Troubleshooting and bug report
==============================

See ``doc/how-to-troubleshoot.txt``. Patches are welcome.


Documentation
=============

Documentation is located in the ``doc`` folder. Start by
``doc/index.txt``. It is also mirrored on `CMFNotification home page`_
on `plone.org`_.

.. _CMFNotification home page: http://plone.org/products/cmfnotification/documentation

.. _plone.org: http://plone.org


Credits
=======

This product has been partially sponsored by `Pilot Systems`_.

The following people have developed, given help or tested this
product:

- Damien Baty (damien AT pilotsystems DOT net - Pilot Systems):
  original author, tests, documentation, maintenance;

- Alex Garel (alexandre AT pilotsystems DOT net - Pilot Systems):
  "labels" feature;

- Gaël Le Mignot (gael AT pilotsystems DOT net - Pilot Systems): bug
  fixes;

- Gaël Pasgrimaud: bug fixes, insightful comments and default mail
  templates in the early days.

Translations:

- Gunter Vasold (gunter DOT vasold AT fh-joanneum DOT at - FH
  Joanneum): translation in German;

- Júlio Monteiro (monteiro AT lab DOT pro DOT br): translation in
  Brazilian Portuguese.

.. _Pilot Systems: http://www.pilotsystems.net


License
=======

This product is licensed under GNU GPL. See 'LICENSE.txt' for further
informations.
