import urllib
import urllib2
import json

url = 'http://54.172.148.221:5000/scrape_companies'

data = [
    {
        'name': 'memsql',
        'linkedin_id': 324 
    },
    {
        'name': 'square',
        'linkedin_id': 2344
    },
    {
        'name': 'twitter',
        'linkedin_id': 123
    },
    {
        'name': 'facebook',
        'linkedin_id': 124
    },
    {
        'name': 'linkedin',
        'linkedin_id': 234324
    },
]

data = urllib.urlencode({'data': json.dumps(data)})
req = urllib2.Request(url, data)
response = urllib2.urlopen(req)
html = response.read()

print html
