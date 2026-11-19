from pathlib import Path
import urllib.request,hashlib,json,numpy as np
root=Path(__file__).resolve().parents[1]
base='https://people.math.sc.edu/Burkardt/datasets/ngrams/'
manifest=[];arrays=[]
for k,name in enumerate(['english_monograms.txt','english_bigrams.txt','english_trigrams.txt'],1):
 p=root/'data/public_ngrams'/name
 if not p.exists():p.write_bytes(urllib.request.urlopen(base+name,timeout=30).read())
 a=np.zeros((26,)*k,dtype=np.float64)
 for line in p.read_text().splitlines():
  word,num=line.split();a[tuple(ord(c)-65 for c in word)]=int(num)
 arrays.append(a)
 manifest.append(dict(file=name,url=base+name,sha256=hashlib.sha256(p.read_bytes()).hexdigest(),entries=len(p.read_text().splitlines()),total=int(a.sum())))
c0,c1,c2=arrays
p0=c0/c0.sum();p1=c1/c1.sum(axis=-1,keepdims=True);p2=c2/c2.sum(axis=-1,keepdims=True)
assert all(np.isfinite(p).all() for p in [p0,p1,p2])
assert all(np.allclose(p.sum(axis=-1),1) for p in [p0,p1,p2])
np.concatenate([p0,p1.ravel(),p2.ravel()]).astype('<f8').tofile(root/'results/transitions.bin')
np.savetxt(root/'results/initial_probabilities.csv',p0,delimiter=',',header='A_to_Z',comments='')
np.savetxt(root/'results/one_letter_transitions.csv',p1,delimiter=',',header=','.join('ABCDEFGHIJKLMNOPQRSTUVWXYZ'),comments='')
np.savetxt(root/'results/two_letter_transitions.csv',p2.reshape(676,26),delimiter=',',header=','.join('ABCDEFGHIJKLMNOPQRSTUVWXYZ'),comments='')
(root/'results/public_sources.json').write_text(json.dumps(manifest,indent=2))
print(json.dumps(manifest,indent=2))
