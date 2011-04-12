#!/usr/bin/env python
#
# googtext 0.1
# Written on 2009-03-27 by Senko Rasic <senko@senko.net>
# This software is Public Domain. Use it as you like.

import gtranslate
import polib
import sys
import re

class GoogText:

    STRINGS_PER_REQUEST = 100

    def __init__(self, client_url, api_key=None):
        self.api = gtranslate.LanguageAPI(client_url, api_key)

    def translate(self, src_file, src_lang, dest_file, dest_lang):
        pofile = polib.pofile(src_file)

        entries = []
        ids = []
        tokens = dict()
        lastnum = 0
        
        dcregex = re.compile('Default: "([^"]*)"',re.DOTALL)
        
        
        for entry in pofile:
            if entry.translated():
                continue
            entries.append(entry)

            # Sorry folks, this will get squashed
            txt = entry.msgid.replace('_', '')
            if entry.comment and entry.comment.startswith('Default: '):
                dcmatches = dcregex.findall(entry.comment)
                if dcmatches and len(dcmatches) > 0:
                    txt = dcmatches[0]
            if len(txt) > 500:
                #We must skip entries longer than this, because google translate complains for these?
                continue
            
            tokenlist = re.findall('(\$\{[^\}]+\})',txt)
            if tokenlist and len(tokenlist)>0:
                #There are $tokens in the msgid string.We will put this into our tokens dict and
                #replace them with (numeric ids) so that when they come back translated we can replace the $tokens back
                for token in tokenlist:
                    lastnum = lastnum + 1
                    id = "GT" + str(lastnum)
                    tokens[id] = token
                    txt = txt.replace(token,id)
            ids.append(txt)

            if len(ids) > self.STRINGS_PER_REQUEST:
                print len(ids), ids
                try:
                    strs = self.api.translate_many(ids, src_lang, dest_lang)
                except Exception as inst:
                    print "Caught Exception: %s" % inst
                    
                    strs = []
                    for id in ids:
                        try:
                            print "Translating: %s" % id
                            ret = self.api.translate(id,src_lang,dest_lang)
                            strs.append(ret)
                        except Exception as inst2:
                            strs.append('')
                            print "Caught Exception %s" %inst2
                    
                strs_replaced = []
                for astr in strs:
                    ttokens = re.findall('(GT\d*)',astr)
                    if ttokens and len(ttokens) > 0:
                        for ttoken in ttokens:
                            print "Finding %s" % ttoken
                            if ttoken in tokens:
                                astr = astr.replace(ttoken,tokens[ttoken])
                    strs_replaced.append(astr)
                assert len(ids) == len(strs_replaced) == len(entries)

                for msg_str, e in zip(strs_replaced, entries):
                    e.msgstr = msg_str.strip()

                ids = []
                entries = []
                tokens = dict()
                lastnum = 0

        pofile.save(dest_file)


if __name__ == '__main__':
    if len(sys.argv) != 5:
        sys.stderr.write('Usage: %s <src.po> <src_lang> <dest.po> <dest_lang>\n' % sys.argv[0])
        sys.exit(-1)

    key = open('/home/dhiraj/src/googtext/googleapikey.txt').read().strip()
    gt = GoogText('http://senko.net/services/googtext/', key)
    gt.translate(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4])
    sys.exit(0)


