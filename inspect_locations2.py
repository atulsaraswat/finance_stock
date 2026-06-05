import urllib.request
import urllib.parse
import json
headers={'User-Agent':'Mozilla/5.0'}
for loc in ['Alpharetta, GA','30005','Atlanta, GA']:
    q=urllib.parse.urlencode({'location':loc,'page':1})
    url='https://www.themuse.com/api/public/jobs?'+q
    req=urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req, timeout=15) as r:
        data=json.load(r)
    locnames=set()
    for job in data.get('results', []):
        for l in job.get('locations', []):
            locnames.add(l.get('name'))
    print(loc, len(data.get('results', [])), sorted(locnames))
