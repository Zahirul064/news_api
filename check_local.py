import json, re, requests, urllib3, concurrent.futures as cf
from urllib.parse import urljoin
urllib3.disable_warnings()
C = json.load(open('cand_local.json'))
H = {'User-Agent': 'Mozilla/5.0 (Linux; Android 13; Pixel 7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Mobile Safari/537.36',
     'Accept-Language': 'bn,en;q=0.8'}
BAD = ['judi', 'slot gacor', 'casino', 'togel', 'betting', 'sbobet', 'buy this domain', 'domain is for sale', 'parked',
       'dynadot', 'hugedomains', 'account suspended', 'default web site', 'airo ai builder', 'domain for sale']
def chk(c):
    r = dict(c)
    for u in (c['url'], c['url'].replace('https://', 'http://')):
        try:
            s = requests.get(u, headers=H, timeout=40, allow_redirects=True, verify=False)
            s.encoding = s.apparent_encoding if not s.encoding or s.encoding.lower() == 'iso-8859-1' else s.encoding
            t = s.text
            m = re.search(r'<title[^>]*>(.*?)</title>', t, re.S | re.I)
            icon = re.search(r'<link[^>]+rel=["\'](?:apple-touch-icon[^"\']*|icon|shortcut icon)["\'][^>]+href=["\']([^"\']+)', t, re.I)
            r.update(status=s.status_code, final=s.url, title=(m.group(1).strip()[:100] if m else ''),
                     bangla=len(re.findall(r'[ঀ-৿]', t)), dist=t.count(c['bn']),
                     y2026=t.count('2026') + t.count('২০২৬'), bad=[k for k in BAD if k in t.lower()],
                     icon=urljoin(s.url, icon.group(1)) if icon else '')
            r.pop('error', None)
            return r
        except Exception as e:
            r['error'] = str(e)[:120]
    return r
with cf.ThreadPoolExecutor(30) as ex:
    res = list(ex.map(chk, C))
json.dump(res, open('report_local.json', 'w'), ensure_ascii=False, indent=1)
