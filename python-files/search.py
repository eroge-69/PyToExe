import asyncio,aiohttp,urllib.parse,re
from selectolax.parser import HTMLParser

B={"wikipedia.org","aol.com","youtube.com","wiktionary.org"}
class A:
 async def __aenter__(s):s.u="https://search.aol.com/aol/search";s.h={'User-Agent':'Mozilla/5.0','Accept':'*/*','Accept-Language':'ru','Connection':'keep-alive'};s.s=aiohttp.ClientSession(headers=s.h);return s
 async def __aexit__(s,*_):await s.s.close()
 async def f(s,q):
  try:return await(await s.s.get(s.u,params={'q':q,'ei':'UTF-8'},timeout=10)).text()
  except:return
 def p(s,h):
  p=HTMLParser(h);c=p.css_first('#results')or p.css_first('.searchCenterMiddle')
  return[r for r in s.x(c)if all(b not in urllib.parse.urlparse(r['url']).netloc.lower()for b in B)]if c else[]
 def x(s,c):
  r=[]
  for l in c.css('ol.mb-15.reg.searchCenterMiddle li')[1:]+c.css('ul.compArticleList li'):
   a=l.css_first('.compTitle h3.title a')or l.css_first('.thmb')or l.css_first('a');u=a.attributes.get('href','')if a else'';t=a.text(strip=True)if a else''
   if not t:
    for x in l.css('a'):
     if x!=a and x.text(strip=True):t=x.text(strip=True);u=x.attributes.get('href','');break
   i=l.css_first('img');th=i.attributes.get('src')if i and i.attributes.get('src','').startswith('http')else None
   d=s.d(l.css_first('.compText'))
   if a and re.search('[а-яА-Я]',d):r+=[{'url':s.r(u),'title':t,'description':d,'thumbnail':th}]
  return r or [{'url':s.r(u),'title':t,'description':d,'thumbnail':th}] if a else []
 def r(s,u):
  if not u or'click'not in u:return u
  try:
   p=urllib.parse.urlparse(u);qp=urllib.parse.parse_qs(p.query);ru=qp.get('RU',[None])[0]
   if ru:return urllib.parse.unquote(ru)
   for x in p.path.split('/'):
    if x.startswith('RU='):return urllib.parse.unquote(x[3:])
  except:return u
  return u
 def d(s,e):
  return re.sub(r'\s+',' ',re.sub(r'[^\w\s\-.,!?():;/]',' ',e.text(separator='\n',strip=True).replace('\n',' '))if e else'').strip()
 def o(s,r,t=None):
  return f"\n📝 {r['title']}\n"+(f"📄 {r['description']}\n"if r['description']else'')+f"🔗 {r['url']}\n"+(f"🖼️ {t}\n"if t else'')

class Wiki:
 def __init__(s):s.h={'User-Agent':'Mozilla/5.0'};s.s=aiohttp.ClientSession()
 async def close(s):await s.s.close()
 async def f(s,q):
  try:
   async with s.s.get(f"https://ru.wikipedia.org/w/index.php?search={q.replace(' ','%20')}&limit=1",headers=s.h)as r:
    p=HTMLParser(await r.text());u=("https://ru.wikipedia.org"+p.css_first('div.mw-search-result-heading a').attributes['href'])if p.css('div.mw-search-result-heading')else(str(r.url)if'/wiki/'in str(r.url)else None)
   if not u:return
   async with s.s.get(u,headers=s.h)as r:
    p=HTMLParser(await r.text());imgs=p.css('img');is_disambig=any('Disambig.svg' in(i.attributes.get('src','')or'')for i in imgs)
    if is_disambig:
     m=[]
     for li in p.css('div.mw-parser-output ul li')[:5]:
      t=li.text();t=re.sub(r'\.mw-parser-output.?}|@media.?}|body\.ns-0.?}','',t)
      for x in['Примечания','Если вы попали','См. также страницы с','Проект «Страницы']:t=t.split(x)[0]
      t=re.sub(r'\[.??]|\s+',' ',t).strip()
      if len(t)>10 and ' — 'in t:m+=[t]
     d='\n'.join(m)or"Значения не найдены"
    else:
     d=' '.join(x.text()for x in p.css('div.mw-parser-output p')[:3]);d=re.sub(r'\[.*?]|\s+',' ',d).strip();d=d[:500]
     for punc in'.!?':
      if punc in d:d=d.rsplit(punc,1)[0]+punc;break
    for i in imgs:
     s=i.attributes.get('src','');w,h=int(i.attributes.get('width',0)),int(i.attributes.get('height',0))
     if any(x in s.lower()for x in['.jpg','.png','.jpeg','.webp'])and all(y not in s for y in['Disambig','Commons','Icon','Symbol'])and w>=100 and h>=100:img='https:'+s if s.startswith('//')else s;break
    return{'url':u,'title':q,'description':d,'thumbnail':img if 'img' in locals()else None}
  except:return

async def g(q):
 try:return(await(await aiohttp.ClientSession().get(f'https://g.tenor.com/v1/search?key=LIVDSRZULELA&locale=ru_RU&limit=1&media_filter=minimal&contentfilter=off&q={q}')).json())['results'][0]['media'][0]['gif']['url']
 except:return

async def main():
 a=Wiki()
 async with A()as x:
  while 1:
   try:
    q=input("Поиск: ").strip()
    if q.lower()in['quit','exit','выход']:break
    if not q:continue
    h=await x.f(q);r=x.p(h)if h else[];fb=0
    if not r:r=[await a.f(q)];fb=1
    if not r or not r[0]:continue
    f=r[0];t=f.get('thumbnail')or await g(q if fb else f['title'])
    print(x.o(f,t))
   except:break
 await a.close()

if __name__=='__main__':asyncio.run(main())