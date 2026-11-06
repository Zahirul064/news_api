import json,re,requests,concurrent.futures as cf
files=['bd_national_news.json','bd_local_news.json','eng_national_news.json','online_news.json','international_news.json','bd_media_news.json']
urls=sorted({x['pdfUrl'] for f in files for x in json.load(open(f))})
H={'User-Agent':'Mozilla/5.0 (Linux; Android 13; Pixel 7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Mobile Safari/537.36'}
KW=['domain is for sale','buy this domain','parked','coming soon','dynadot','sedo','godaddy','hugedomains','account suspended','under construction','default web site page','index of /','this domain','website is under','suspended']
def chk(u):
  r={'url':u}
  try:
    s=requests.get(u,headers=H,timeout=25,allow_redirects=True)
    t=s.text
    m=re.search(r'<title[^>]*>(.*?)</title>',t,re.S|re.I)
    r.update(status=s.status_code,final=s.url,title=(m.group(1).strip()[:150] if m else ''),size=len(t),
      bangla=len(re.findall(r'[ঀ-৿]',t)),links=len(re.findall(r'<a\s',t,re.I)),
      kw=[k for k in KW if k in t.lower()])
  except Exception as e: r['error']=str(e)[:200]
  return r
with cf.ThreadPoolExecutor(20) as ex: res=list(ex.map(chk,urls))
json.dump(res,open('report.json','w'),ensure_ascii=False,indent=1)
