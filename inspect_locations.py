import urllib.request
import urllib.parse
import json
headers={'User-Agent':'Mozilla/5.0'}
q=urllib.parse.urlencode({'location':'Alpharetta','page':1})
url='https://www.themuse.com/api/public/jobs?'+q
req=urllib.request.Request(url, headers=headers)
with urllib.request.urlopen(req, timeout=15) as r:
    data=json.load(r)
locnames=set()
for job in data.get('results', []):
    for loc in job.get('locations', []):
        locnames.add(loc.get('name'))
print(sorted(locnames))
