#!/bin/sh
TEMPLATES=`find ../skins -iregex '.*\..?pt'`

echo "Warning!! Be sure that i18ndude contains 'merge' parameter"

i18ndude rebuild-pot --pot ./at_ratings.pot --create at_ratings --merge ./manual.pot  $TEMPLATES
i18ndude sync --pot ./at_ratings.pot ./at_ratings-??.po

i18ndude sync --pot ./at_ratings_plone.pot ./at_ratings_plone-??.po


