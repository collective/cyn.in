i18ndude rebuild-pot --pot ./cmfnotification.pot --create cmfnotification ../ || exit 1
i18ndude sync --pot ./cmfnotification.pot ./cmfnotification-*.po

i18ndude rebuild-pot --pot ./plone.pot --create plone ../ || exit 1
i18ndude sync --pot ./plone.pot ./plone-*.po

ERRORS=`find ../ -name "*pt" | xargs i18ndude find-untranslated | grep -e '^-ERROR' | wc -l`
WARNINGS=`find ../ -name "*pt" | xargs i18ndude find-untranslated | grep -e '^-WARN' | wc -l`
FATAL=`find ../ -name "*pt"  | xargs i18ndude find-untranslated | grep -e '^-FATAL' | wc -l`

echo
echo "There are $ERRORS errors \(almost definitely missing i18n markup\)"
echo "There are $WARNINGS warnings \(possibly missing i18n markup\)"
echo "There are $FATAL fatal errors \(template could not be parsed, eg. if it\'s not html\)"
echo "For more details, run \'find . -name \"\*pt\" \| xargs i18ndude find-untranslated\' or" 
echo "Look the rebuild i18n log generate for this script called \'rebuild_i18n.log\' on locales dir" 

rm ./rebuild_i18n.log
touch ./rebuild_i18n.log

find ../ -name "*pt" | xargs i18ndude find-untranslated > ./rebuild_i18n.log
