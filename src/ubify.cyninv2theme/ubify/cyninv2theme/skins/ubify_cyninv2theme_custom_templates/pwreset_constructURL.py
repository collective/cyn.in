## Script (Python) "pwreset_constructURL.py"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##title=Create the URL where passwords are reset
##parameters=randomstring,userid=None
site_properties = container.portal_properties.site_properties
if hasattr(site_properties,'email_verification_url') and site_properties.email_verification_url != '':    
    evurl = site_properties.email_verification_url
    if userid is not None:
        evurl = evurl.replace('$userid',userid)
    evurl = evurl.replace('$code',randomstring)
    return evurl
else:
    host = container.absolute_url()
    rUrl = "%s/passwordreset/%s" % (host,randomstring)
    if userid is not None:
        rUrl = rUrl + "?userid=%s" % (userid,)
    return  rUrl
