#!/usr/bin/env python3
from pathlib import Path
import urllib.request, concurrent.futures, re, hashlib, json
ROOT=Path(__file__).resolve().parents[1]
BOOKS={11:'alice',1342:'pride_and_prejudice',84:'frankenstein',2701:'moby_dick',1661:'sherlock_holmes',76:'huckleberry_finn'}
def fetch(item):
 name,url=item; p=ROOT/'sources'/name
 with urllib.request.urlopen(url,timeout=120) as f: p.write_bytes(f.read())
 return {'file':str(p.relative_to(ROOT)),'url':url,'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'bytes':p.stat().st_size}
REPOS={11:'Alice-s-Adventures-in-Wonderland_11',1342:'Pride-and-Prejudice_1342',84:'Frankenstein_84',2701:'Moby-Dick--Or-The-Whale_2701',1661:'The-Adventures-of-Sherlock-Holmes_1661',76:'Adventures-of-Huckleberry-Finn_76'}
items=[(f'english_{n}grams.txt',f'https://people.math.sc.edu/Burkardt/datasets/ngrams/english_{n}grams.txt') for n in ['mono','bi','tri','quad']]+[(f'{v}_{k}.txt',f'https://raw.githubusercontent.com/GITenberg/{REPOS[k]}/master/{k}' + ('.txt' if k in (84,1661) else '-0.txt')) for k,v in BOOKS.items()]
with concurrent.futures.ThreadPoolExecutor(max_workers=8) as ex: meta=list(ex.map(fetch,items))
for k,v in BOOKS.items():
 p=ROOT/'sources'/f'{v}_{k}.txt'; s=p.read_text(encoding='utf-8-sig')
 start=re.search(r'^\*\*\* START OF (?:THE|THIS) PROJECT GUTENBERG EBOOK.*?\*\*\*',s,re.M)
 end=re.search(r'^\*\*\* END OF (?:THE|THIS) PROJECT GUTENBERG EBOOK.*?\*\*\*',s,re.M)
 if not start or not end: raise ValueError(('markers',p))
 s=s[start.end():end.start()]
 s=''.join(c.upper() for c in s if ('a'<=c<='z' or 'A'<=c<='Z'))
 (ROOT/'data'/f'{v}.txt').write_text(s)
 print(v,len(s),flush=True)
(ROOT/'data'/'provenance.json').write_text(json.dumps(meta,indent=2))
