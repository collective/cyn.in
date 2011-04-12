#!/bin/bash

# List of languages
LANGUAGES="th ko hi uk id mt fr lv gl vi hr af ru ca zh tr sk sr pt it es lt de mk be fi zh-tw sw is nl bg no da et sv ja pt-br cy hu ga cs sq ro pl "
DOMAIN="cynin"
EXTRA=""
CATALOGNAME=${DOMAIN}

# Create locales folder structure for languages
for lang in $LANGUAGES; do
	install -d $lang/LC_MESSAGES
done

# Compile po files
for lang in $(find . -mindepth 1 -maxdepth 1 -type d); do

    if test -d $lang/LC_MESSAGES; then
    		
		PO=$lang/LC_MESSAGES/$DOMAIN.po

    	# Create po file if not exists
    	touch $PO 

		# Sync po file
		echo "Syncing $PO"
		~/venv/bin/i18ndude sync --pot $DOMAIN.pot $PO

                # Compile .po to .mo
                MO=$lang/LC_MESSAGES/${CATALOGNAME}.mo
                echo "Compiling $MO"
                msgfmt -o $MO $lang/LC_MESSAGES/${CATALOGNAME}.po

    fi
done
