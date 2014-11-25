# -*- coding: utf-8 -*-
import urllib2
from time import sleep
from random import randint

CRUNCHBASE_USER_KEYS = [
    '777bdddfa10b5b8ef896e4be26ebd75c',
    '4c004a9cb5fafe3f5e95368fc4d4566a',
    '784bfbfbc2e0c8b603a2855e7cad22a8',
    '5ca12f415dd21b1b9f907c83b68d2fc6',
    '9857353db9f1a2639e8638587e0551ce',
    '3cb5270a4777257ea393ccfd94eec3c5',
    '1e0d2ce5cb65a9a08a296b1b47759cb6',
    'e4e46e931052bb3d1e3c50e93eed2623',
    '14915aa4e3ee1b014e7ca54cff8baca4',
    'c124410233e33eb99ea2031c865cc1cc',
    'fecbcd7d48019fb02a983e04d50cb1c4'
]

class CrunchBaseAPI:
    url_template = u'http://api.crunchbase.com/v/2/{0}?user_key={1}{2}'
    orders = [
        'created_at+DESC',
        'created_at+ASC',
        'updated_at+DESC',
        'updated_at+ASC'
    ]

    def _next_key(self):
        self.user_key_idx += 1
        if self.user_key_idx >= len(CRUNCHBASE_USER_KEYS):
            self.user_key_idx = 0
        self.user_key = CRUNCHBASE_USER_KEYS[self.user_key_idx]

    def __init__(self):
        self.user_key_idx = 0
        self.user_key = CRUNCHBASE_USER_KEYS[self.user_key_idx]

    def get(self, operation, params=dict()):
        other = "".join(['&' + str(k) + '=' + str(v) for k, v in params.iteritems()])
        # keep trying different user_keys until it works...
        # this is to hack around the 2500 api calls per day limit
        # try the whole range of keys three times before giving up
        for attempt in range(len(CRUNCHBASE_USER_KEYS * 3)):
            url = CrunchBaseAPI.url_template.format(operation, self.user_key, other, )
            print '                            url = ' + url
            wait_secs = randint(1, 10)
            result = None
            # keep trying the same key, increasing the wait interval on failures
            # this is to hack around the 40 calls per minute limit
            while not result and wait_secs < 600:
                try:
                    print '                                     waiting for ' + str(wait_secs) + ' sconds..'
                    sleep(wait_secs)
                    result = urllib2.urlopen(url.encode('utf8')).read()
                    if not result:
                        wait_secs *= 2
                        print '                     NO RESULT; waiting ' + str(wait_secs) + ' seconds and trying again...'
                except:
                    wait_secs *= 2
                    print '                    FAILED; waiting ' + str(wait_secs) + ' seconds and trying again...'

            # if we failed with the current key, move on to a different one
            if not result:
                self._next_key()
                print '   .... this FUCKING user_key won\'t work; moving on to next one: ' + str(self.user_key_idx) + ' -> ' + str(self.user_key)
            # if we succeeded, exit the for loop and return result
            else:
                break

        if not result:
            print 'FUUUUUUUUUUUUCK.... couldn\'t get it working after trying each key 3 times... returning None.... #fail #SHIT #fuckcrunchbase'
        return result

crunchbase = CrunchBaseAPI()
