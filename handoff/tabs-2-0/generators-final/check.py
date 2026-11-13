import subprocess,json
from data import E
ua="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126 Safari/537.36"
urls=sorted({u.split('#')[0] for e in E for _,u in e[2]})
from concurrent.futures import ThreadPoolExecutor
def c(u):
  r=subprocess.run(["curl","-sL","-A",ua,"-m","30","-o","/tmp/b","-w","%{http_code} %{url_effective}",u],capture_output=True,text=True)
  body=open('/tmp/b','rb').read()[:200000].decode('utf8','ignore').lower() if r.stdout else ''
  return u,r.stdout
res=dict(ThreadPoolExecutor(8).map(c,urls))
json.dump(res,open('status.json','w'),indent=1)
for u,s in res.items(): print(s.split()[0] if s else 'ERR',u, '' if not s or s.split()[1]==u else '-> '+s.split()[1])
