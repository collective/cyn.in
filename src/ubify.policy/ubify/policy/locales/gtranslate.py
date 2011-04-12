#!/usr/bin/env python
#
# gtranslate 0.1
# Written on 2009-03-27 by Senko Rasic <senko@senko.net>
# This software is Public Domain. Use it as you like.

"""
Support for Google Language AJAX API.

A thin wrapper around Google Language AJAX API
(see http://code.google.com/apis/ajaxlanguage/documentation/).
"""

import json
import urllib

class TranslationError(Exception):
    pass

class LanguageAPI:

    BASE_URL = 'http://ajax.googleapis.com/ajax/services/language/'

    def __init__(self, client_url, api_key=None):
        """
        Create a new LanguageAPI() instance. The client_url
        parameter should be set to the URL of the service using
        the API, and is sent as referer to Google. If you have
        Google API key, set it as the second parameter.
        """

        self.referer = client_url
        self.api_key = api_key

    def _send_request(self, service, data):
        """
        Sends the POST request to the service.
        """

        data.append(('v', '1.0'))

        if self.api_key:
            data.append(('key', self.api_key))

        opener = urllib.URLopener()

        if self.referer:
            opener.addheader('Referer', self.referer)

        post_parts = [ '%s=%s' % (k, urllib.quote_plus(v))
            for k, v in data ]
        post_data = '&'.join(post_parts)

        url = self.BASE_URL + service
        raw = opener.open(url, post_data).read()
        resp = json.read(raw.decode('utf-8'))

        if resp['responseStatus'] != 200:
            raise TranslationError(resp['responseDetails'])

        return resp['responseData']


    def translate(self, text, from_lang, to_lang):
        """
        Translate a chunk of text. Use two-letter language code for
        selecting source and target languages. If the 'from_lang' parameter
        is None, the service will try and autodetect the source
        language. Returns translated text.
        """

        if from_lang is None:
            from_lang = ''

        resp = self._send_request('translate', {
            'langpair': '%s|%s' % (from_lang, to_lang),
            'q': text
        }.items())

        return resp['translatedText']

    def translate_many(self, text_list, from_lang, to_lang):
        """
        Translate several chunks of text. Lang parameters are
        the same as in the translate() method. Returns a list
        of translated texts. If a particular text can't be
        translated, None is returned instead.
        """

        if from_lang is None:
            from_lang = ''

        data = [ ('langpair', '%s|%s' % (from_lang, to_lang)) ]
        for text in text_list:
            data.append(('q', text))

        results = []
        for r in self._send_request('translate', data):
            if r['responseStatus'] == 200:
                results.append(r['responseData']['translatedText'])
            else:
                results.append(None)

        return results

    def detect(self, text):
        """
        Detect language of the text.
        """

        resp = self._send_request('detect', {'q': text})

        return resp

