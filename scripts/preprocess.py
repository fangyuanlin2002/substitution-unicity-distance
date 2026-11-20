"""Verify bundled snapshots and deterministically regenerate cleaned corpus."""
from pathlib import Path
import hashlib,json,re
ROOT=Path(__file__).resolve().parents[1]
for r in json.loads((ROOT/'data/provenance.json').read_text()):
 path=ROOT/r['file'];assert hashlib.sha256(path.read_bytes()).hexdigest()==r['sha256'],path
books={11:'alice',1342:'pride_and_prejudice',84:'frankenstein',2701:'moby_dick',1661:'sherlock_holmes',76:'huckleberry_finn'}
total=0
for k,v in books.items():
 p=ROOT/'sources'/f'{v}_{k}.txt';s=p.read_text(encoding='utf-8-sig')
 start=re.search(r'^\*\*\* START OF (?:THE|THIS) PROJECT GUTENBERG EBOOK.*?\*\*\*',s,re.M)
 end=re.search(r'^\*\*\* END OF (?:THE|THIS) PROJECT GUTENBERG EBOOK.*?\*\*\*',s,re.M)
 assert start and end,p
 s=''.join(c.upper() for c in s[start.end():end.start()] if ('a'<=c<='z' or 'A'<=c<='Z'))
 (ROOT/'data'/f'{v}.txt').write_text(s);total+=len(s)
assert total==2791233,total
print('Verified all snapshot hashes and corpus preprocessing:',total,'letters')
