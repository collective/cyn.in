## Script (Python) "rateContent"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=rating=None
##title=
##

request = context.REQUEST

prefix = 'rating_'
for key in request.form:
    if key.startswith(prefix):
        rating = key[len(prefix):].split('.')[0]
        break
uid = context.UID()
context.portal_ratings.addRating(int(rating), uid)
view_url = context.absolute_url() + '/view'

request.RESPONSE.redirect(view_url + '?portal_status_message=Thanks for your vote!')
