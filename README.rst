###############################################################################
cyn.in is an open source Collaborative Knowledge Management Appliance that 
enables teams to seamlessly work together on files, documents and content in 
a secure central environment.

cyn.in v2 an open source appliance is distributed under the GPL v3 license 
along with commercial support options.

cyn.in is a Cynapse Invention.

Copyright (C) 2008 Cynapse India Pvt. Ltd.

This program is free software: you can redistribute it and/or modify it under
the terms of the GNU General Public License as published by the Free Software 
Foundation, either version 3 of the License, or any later version and observe 
the Additional Terms applicable to this program and must display appropriate 
legal notices. In accordance with Section 7(b) of the GNU General Public 
License version 3, these Appropriate Legal Notices must retain the display of 
the "Powered by cyn.in" AND "A Cynapse Invention" logos. You should have 
received a copy of the detailed Additional Terms License with this program.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of 
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General 
Public License for more details.

You should have received a copy of the GNU General Public License along with 
this program.  If not, see <http://www.gnu.org/licenses/>.

You can contact Cynapse at support@cynapse.com with any problems with cyn.in. 
For any queries regarding the licensing, please send your mails to 
 legal@cynapse.com

You can also contact Cynapse at:
802, Building No. 1,
Dheeraj Sagar, Malad(W)
Mumbai-400064, India
###############################################################################

WELCOME TO CYN.IN
-----------------------------------------
cyn.in is based upon the open source plone platform. While a complete 
understanding of plone does help (a lot) it is not abosolutely essential to run
cyn.in.

REQUIREMENTS
------------

Operating System
=================
While it is possible to do a buildout successfully on the Microsoft Windows 
operating system, it is not recommended - that way is fraught with difficulty and
strife. 

Instead we recommend any linux distribution (we recommend Ubuntu 8.0.4) for doing
development on cyn.in as this provides the easiest and most rewarding path to developing
on cyn.in.

While we actively use Ubuntu, Debian and rPath linux to develop cyn.in there's no reason
that it should not work on any linux distribution that supports running python.


Dependency installation for Cyn.in Source Buildout
==================================================
Table of Contents

       1. Cyn.in Dependency installation using Package Managers
             1. Ubuntu 8.0.4 (Hardy)
             2. Ubuntu 8.1.0 (Intrepid) and Debian 5.0 (Lenny)
             3. Ubuntu 9.0.4 (Jaunty)
       2. Make a new virtualenv for your login
       3. Install python dependencies to your VirtualEnv
       4. Do Bootstrap
       5. Do Buildout

1. Cyn.in Dependency installation using Package Managers

1.1 Ubuntu 8.0.4 (Hardy)

sudo apt-get build-dep python-ldap python-lxml build-essential gcc g++ libc6-dev libssl-dev zlib1g-dev libjpeg62-dev libreadline5-dev readline-common wv python2.4-dev poppler-utils python-imaging python-libxml2 libxml2-dev libxslt1-dev subversion libdb4.4-dev libldap2-dev libsasl2-dev libssl-dev python-ldap python-setuptools


1.2 Ubuntu 8.1.0 (Intrepid) and Debian 5.0 (Lenny)
sudo apt-get install build-essential gcc g++ libc6-dev libssl-dev zlib1g-dev libjpeg62-dev libreadline5-dev readline-common wv python2.4-dev poppler-utils python-imaging python-libxml2 libxml2-dev libxslt1-dev subversion libsasl2-dev libssl-dev python-ldap libdb-dev libldap2-dev python-setuptools

1.3 Ubuntu 9.04 (Jaunty) - should work for 9.10 (Karmic) as well.
sudo apt-get install build-essential libssl-dev libjpeg62-dev libreadline5-dev wv  libxml2-dev libxslt1-dev libsasl2-dev poppler-utils libdb4.4-dev libldap2-dev python2.4-dev

2. Make a new virtualenv for your login

After getting dependencies using your package manager, checkout any cyninsrc branch/trunk. 
From this, you'll find a file, ez_setup.py, you have to run this to install easy_install:

    sudo python2.4 ez_setup.py

Next, we install virtualenv which will be used for installing required python dependencies of cyn.in:

sudo easy_install-2.4 virtualenv

Lets start by making a virtualenv based virtual python environment for our own usermode python installation:

virtualenv --python=python2.4 -v --no-site-packages ~/venv

This makes a local python install at ~venv which we will now use to do the buildout. First we need to easy_install the dependencies.
Install python dependencies to your VirtualEnv

3. Use this concatenated command that will easy_install all dependencies together.

    ~/venv/bin/easy_install-2.4 ZopeSkel && ~/venv/bin/easy_install-2.4 lxml && ~/venv/bin/easy_install-2.4 python-ldap && ~/venv/bin/easy_install-2.4 -i http://dist.serverzen.com/pypi/simple PILwoTk

4. Do Bootstrap

That's it for the dependencies, you're ready to do the buildout, just take care to use the venv python2.4 instead of the system-wide one.

cd to your buildout directory (it must have bootstrap.py and buildout.cfg in it) and:

    ~/venv/bin/python2.4 bootstrap.py


A note on Python
================
cyn.in REQUIRES to be run on python2.4 it will not work properly on earlier OR
later versions of python.

You can type ~/venv/bin/python -V on your command prompt to see your current version of python.

BUILDOUT
---------------
The zip file containing the source of the cyn.in package is what is referred to
as a "buildout". This is a complete system for building and managing instances
of cyn.in.

More details on this are available here: http://pypi.python.org/pypi/zc.buildout

Extract the zip file to a suitable location and cd to it.
Edit user.cfg and change the effective-user setting to your username. For example
if you login with the user dhiraj then the line would read:

effective-user = dhiraj

Next you have to build the buildout - this will require a good Internet connection
because all required components will be downloaded automatically.

Run the following comand in the same directory:

./bin/buildout -c user.cfg

This will display scrolling progress of buildout and will take a LOT of time, especially the
first time you do this.

RUNNING FOR THE FIRST TIME
---------------------------
When your buildout is complete, you can start the zope server by typing:

./bin/instance fg

This will start the zope server in foreground mode (so that you can easily
kill it by pressing Ctrl + C).

Read the scrolling output, if all goes well you will see something like 
the following when the scrolling stops:
"2008-07-14 13:58:25 INFO Zope Ready to handle requests"

Congratulations, you've managed to get over the difficult parts. Now for the 
easy / fun stuff:
Open up your favorite browser (Everybody say together with me: Firefox!) :)

Navigate to http://localhost:8080 (if you use the same computer as desktop) or 
substitute the localhost with the hostname (or even the IP address) of the 
computer that zope/cyn.in is running on.

You should see the "Zope quick start screen". Cool, you can access your newly
built Zope server. Next, navigate to http://localhost:8080/manage .

This will give you an HTTP basic auth request. Use the following credentials 
to get in:
username: admin
password: secret

You will see the standard Zope management interface. On the right you will see
a drop down list, next to a button labeled 'Add'.

From the list, scroll down and select "Plone Site", and you'll get the Add Plone
Site screen. Type in an ID for the plone site (I recommend cynin) and hit the
Add Plone Site button - do not change anything else.

This will take some time, if you're feeling geeky you can watch the scrolling 
text in your fg command line window to see what's going on.

After some time your browser will arrive back at the zope management screen, with
one major difference, you'll see a new entry in the left tree view as well as
in the center list, cynin (Site).
Great, you've succeeded in adding a new plone site. Click on it.

Now, scroll down, and find the item called portal_quickinstaller (Allows to
install/uninstall products) and click on that.

You'll get a list of installable products, among these check the checkbox next
to the item labeled "Ubify Site Policy" and hit the Install button. Do NOT check
any other item.

Again, this will take some time and you can watch the scrolling progress in your
fg command line window. When it completes, the list will refresh where most of 
the items will have moved down to the "Installed Products" section.

Great, you don't know it yet, but you've managed to get a working cyn.in 
installation built out of source! :)

Let's get to proving that: In your browser, type up the following address:
http://localhost:8080/cynin

If you don't like doing as recommended and chose a different ID during Plone 
Site creation, substitue your ID in place of cyin in the above URL, of course.

After some moments of tense waiting, the familiar cyn.in login screen should
greet you and you can get in by using the following standard credentials:

username: siteadmin
password: secret

NEXT STEPS AND CONTRIBUTIONS
----------------------------
Follow the Administration guide at: http://www.cynapse.com/resources/cynin-administration-guide

There's a lot of continuous documentation, tips, walk-throughs and How-Tos being
built at the cynapse community.

If you're not already familiar with plone I suggest the following recommended
reading:

The plone.org documentation section: http://plone.org/documentation
Read up on plone books: http://plone.org/documentation/books
The most recommended book is of course Martin Aspeli's famous "Professional
Plone Development" http://www.packtpub.com/Professional-Plone-web-applications-CMS/book

If you like the product and would like to contribute, or join us in the effort do 
drop us a mail at devel@cynapse.com. Note this email is for developers and 
contributors ONLY, do NOT put your support requests here.


SUPPORT & LINKS
------------------------------------------
From installation, implementation-to-launch and even beyond, Cynapse is committed 
to our customers on-going success. We provide access to skilled support engineers 
coupled with flexible, easy-to-use resources for effective assistance.

Cynapse Customer Care Portal is available exclusively to customers. It is the 
primary resource for information & technical support for deploying and 
maintaining your cyn.in:

    * Product Subscription Management
    * Product order history
    * Invoice & Profile management
    * Support Ticket System
    * Official Knowledge base
    * Official Technical documentation

Please visit http://www.cynapse.com/cynin for more information on cyn.in
Professional Support can be purchased from http://www.cynapse.com/store


Cynapse Community
-----------------
Participate in the Cynapse community! Join us!
We want anyone and everyone who has interest in Cyn.in to register an account at the Cynapse community and tell us what you think.
http://www.cynapse.com/community