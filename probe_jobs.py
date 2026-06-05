import urllib.request
import urllib.parse
import json
headers={'User-Agent':'Mozilla/5.0'}
for loc in ['Alpharetta','Remote','United States']:
    q=urllib.parse.urlencode({'location':loc,'page':1})
    url='https://www.themuse.com/api/public/jobs?'+q
    req=urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req, timeout=15) as r:
        data=json.load(r)
    print(loc, 'count', len(data.get('results', [])))
    print('sample', data.get('results', [])[0].get('name') if data.get('results') else 'none')
