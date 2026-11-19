from pathlib import Path
import numpy as np,itertools,json
root=Path(__file__).resolve().parents[1];v=np.fromfile(root/'results/transitions.bin',dtype='<f8');p=v[:26];T=v[26:702].reshape(26,26);A=v[702:].reshape(26,26,26)
def q(x):return p[x[0]]*T[x[0],x[1]]*np.prod([A[x[i-2],x[i-1],x[i]] for i in range(2,len(x))])
x=[ord(c)-65 for c in 'THAT'];qx=q(x);qs=sum(q([a,b,c,a]) for a,b,c in itertools.permutations(range(26),3));M=100
r=dict(plaintext='THAT',pattern='0120',p_T=p[19],T_TH=T[19,7],A_THA=A[19,7,0],A_HAT=A[7,0,19],Qx=qx,Qs=qs,information_bits=-np.log2(qs),M=M,conditional_unique=(1-qs+qx)**(M-1))
(root/'results/worked_example.json').write_text(json.dumps(r,indent=2));print(r)
