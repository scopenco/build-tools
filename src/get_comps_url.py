#!/usr/bin/env python
# (c) 2009 Andrey V. Scopenco andrey@scopenco.net
'''
Get url for comps.xml from repomd.xml metadata.

Usage:
    ./get_comps_url.py http://mirror/repodata/repomd.xml

'''

import urllib2
from xml.dom.minidom import parse
from sys import exit, argv

def get_comps(url):

    try: 
        response = urllib2.urlopen(url)
    except urllib2.HTTPError, e:
        print (url + ' return HTTPError = ' + str(e.code))
        exit(1)
    except Exception:
        import traceback
        print ('generic exception: ' + traceback.format_exc())
        exit(1)

    dom = parse(response)
    locations = dom.getElementsByTagName('location')
    for location in locations:
        href = location.attributes['href'].value
        if href.endswith('-comps.xml'):
            request_url = '/'.join(url.split('/')[:-2])
            return request_url + '/' + href

if __name__ == '__main__':
    if len(argv) > 1:
        for url in argv[1:]:
            print get_comps(url)
    else:
        exit(__doc__)
