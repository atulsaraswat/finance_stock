import urllib.request
import json
for url in [
    'https://remoteok.com/api',
    'https://jobs.github.com/positions.json?location=remote',
    'https://www.themuse.com/api/public/jobs?page=1',
]:
    try:
        req=urllib.request.Request(url, headers={'User-Agent':'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=20) as res:
            print('OK', url, res.status)
            data=res.read(500)
            print(data[:200])
    except Exception as e:
        print('ERR', url, type(e).__name__, e)
