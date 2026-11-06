import json,re,requests,concurrent.futures as cf
C=json.load(open('cand.json'))
H={'User-Agent':'Mozilla/5.0 (Linux; Android 13; Pixel 7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Mobile Safari/537.36','Accept-Language':'bn,en;q=0.8'}
BAD=['judi','slot','casino','togel','gacor','betting','sbobet','for sale','buy this domain','parked','dynadot','hugedomains','account suspended','default web site','airo ai builder']
def get(u):
  return requests.get(u,headers=H,timeout=20,allow_redirects=True)
def chk(c):
  r=dict(c)
  for u in [c['url'], c['url'].replace('https://','http://')]:
    try:
      s=get(u); s.encoding=s.apparent_encoding if not s.encoding or s.encoding.lower()=='iso-8859-1' else s.encoding
      t=s.text; low=t.lower()
      m=re.search(r'<title[^>]*>(.*?)</title>',t,re.S|re.I)
      r.update(status=s.status_code,final=s.url,title=(m.group(1).strip()[:120] if m else ''),bangla=len(re.findall(r'[ঀ-৿]',t)),
               dist=t.count(c['bn']),bad=[k for k in BAD if k in low])
      return r
    except Exception as e: r['error']=str(e)[:100]
  return r
with cf.ThreadPoolExecutor(40) as ex: res=list(ex.map(chk,C))
ok=[x for x in res if x.get('status',999)<400 and x.get('bangla',0)>=800 and x.get('dist',0)>=3 and not x.get('bad')]
cf_=[x for x in res if x.get('status') in (403,503) and 'Just a moment' in x.get('title','')]
json.dump({'ok':ok,'cloudflare':cf_,'n':len(res)},open('report.json','w'),ensure_ascii=False,indent=1)
