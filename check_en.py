import json, re, requests, concurrent.futures as cf
from urllib.parse import urljoin, urlparse
C = json.load(open('cand_en.json'))
H = {'User-Agent': 'Mozilla/5.0 (Linux; Android 13; Pixel 7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Mobile Safari/537.36',
     'Accept-Language': 'en,bn;q=0.6'}
BAD = ['judi', 'slot gacor', 'casino', 'togel', 'betting', 'sbobet', 'for sale', 'buy this domain', 'parked',
       'dynadot', 'hugedomains', 'account suspended', 'default web site', 'airo ai builder', 'domain is for sale']

def meta(t, base):
    def find(pats):
        for p in pats:
            m = re.search(p, t, re.I | re.S)
            if m: return urljoin(base, m.group(1).strip())
        return ''
    return {
        'og_image': find([r'<meta[^>]+property=["\']og:image["\'][^>]+content=["\']([^"\']+)',
                          r'<meta[^>]+content=["\']([^"\']+)["\'][^>]+property=["\']og:image["\']']),
        'touch': find([r'<link[^>]+rel=["\']apple-touch-icon[^"\']*["\'][^>]+href=["\']([^"\']+)',
                       r'<link[^>]+href=["\']([^"\']+)["\'][^>]+rel=["\']apple-touch-icon']),
        'icon': find([r'<link[^>]+rel=["\'](?:shortcut )?icon["\'][^>]+href=["\']([^"\']+)',
                      r'<link[^>]+href=["\']([^"\']+)["\'][^>]+rel=["\'](?:shortcut )?icon["\']']),
        'site_name': (re.search(r'<meta[^>]+property=["\']og:site_name["\'][^>]+content=["\']([^"\']+)', t, re.I) or [None, ''])[1],
    }

def chk(u):
    r = {'url': u}
    try:
        s = requests.get(u, headers=H, timeout=40, allow_redirects=True)
        s.encoding = s.apparent_encoding if not s.encoding or s.encoding.lower() == 'iso-8859-1' else s.encoding
        t = s.text
        text = re.sub(r'<script.*?</script>|<style.*?</style>|<[^>]+>', ' ', t, flags=re.S | re.I)
        m = re.search(r'<title[^>]*>(.*?)</title>', t, re.S | re.I)
        r.update(status=s.status_code, final=s.url, title=(m.group(1).strip()[:120] if m else ''),
                 en_words=len(re.findall(r'\b[A-Za-z]{3,}\b', text)), bangla=len(re.findall(r'[ঀ-৿]', text)),
                 y2026=t.count('2026'), y2026bn=t.count('২০২৬'), bad=[k for k in BAD if k in t.lower()], size=len(t))
        r.update(meta(t, s.url))
    except Exception as e:
        r['error'] = str(e)[:150]
    return r

with cf.ThreadPoolExecutor(30) as ex:
    res = list(ex.map(chk, C))
json.dump(res, open('report_en.json', 'w'), ensure_ascii=False, indent=1)
