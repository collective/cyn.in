#!/bin/bash
~/venv/bin/i18ndude rebuild-pot --pot cynin.pot --create cynin --merge manual.pot --exclude="rss.xml.pt itunes.xml.pt" ../../../.. ../../../../../products
###~/venv/bin/i18ndude sync --pot cynin.pot `find . -iname 'cynin*\.po'`
