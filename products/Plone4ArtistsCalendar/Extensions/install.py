from p4a.plonecalendar import sitesetup as calsetup

def install(portal):
    calsetup.setup_portal(portal)

def uninstall(portal, reinstall):
    if not reinstall:
        calsetup.unsetup_portal(portal)
