import urllib.request
import json
url='https://remotive.io/api/remote-jobs'
req=urllib.request.Request(url, headers={'User-Agent':'Mozilla/5.0'})
res=urllib.request.urlopen(req, timeout=20)
data=json.load(res)
res.close()
print(data.keys())
print(len(data.get('jobs', [])))
print(list(data.get('jobs', [])[0].keys())[:20])
