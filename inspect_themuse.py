import urllib.request
import urllib.parse
import json
headers={'User-Agent':'Mozilla/5.0'}
for loc in ['Alpharetta','Remote']:
    q=urllib.parse.urlencode({'location':loc,'page':1})
    url='https://www.themuse.com/api/public/jobs?'+q
    req=urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req, timeout=15) as r:
        data=json.load(r)
    print('LOC', loc, 'count', len(data.get('results', [])))
    if data.get('results'):
        job=data['results'][0]
        print('TITLE', job.get('name'))
        print('LOCATIONS', [loc.get('name') for loc in job.get('locations', [])])
        print('TYPE', job.get('job_type'))
        print('COMPANY', job.get('company', {}).get('name'))
        print('LEVELS', [lvl.get('name') for lvl in job.get('levels', [])])
        print('CATEGORIES', [cat.get('name') for cat in job.get('categories', [])])
        print('DOMAINS', [dom.get('name') for dom in job.get('domains', [])])
        print('QUAL', job.get('publication_date'))
        print('URL', job.get('refs', {}).get('landing_page'))
        print('DESC', job.get('contents', '')[:400])
