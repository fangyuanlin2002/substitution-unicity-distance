#!/usr/bin/env python3
"""Exact finite-alphabet audit of the formula and production C++ class accounting.

Enumerates every iid codebook on alphabet {0,1,2}, with letter probabilities
(1,2,3)/6, for N=1,2,3 and M=1,2,3. Retains duplicate entry multiplicities.
All theoretical probabilities and enumeration weights are rational integers.
The production C++ encode/statistics functions are tested through a temporary
harness; no copied implementation is substituted for those functions.
"""
from pathlib import Path
from fractions import Fraction
from itertools import product, permutations
import subprocess, tempfile, json, math
ROOT = Path(__file__).resolve().parents[1]

def pattern(word):
    seen = {}
    return tuple(seen.setdefault(a,len(seen)) for a in word)

def exact(n,m):
    words=list(product(range(3),repeat=n))
    q={w:Fraction(math.prod(a+1 for a in w),6**n) for w in words}
    s={w:pattern(w) for w in words}
    formula=sum(q[w]*(1-sum(q[v] for v in words if s[v]==s[w] and v!=w))**(m-1) for w in words)
    numerator=0
    for book in product(words,repeat=m):
        good=sum(all(v==w or s[v]!=s[w] for v in book) for w in book)
        numerator+=good*math.prod(math.prod(a+1 for a in w) for w in book)
    enumeration=Fraction(numerator,m*6**(n*m))
    assert formula==enumeration,(n,m,formula,enumeration)
    return formula,numerator

def main():
    # Independently enumerate actual permutation keys for every pair x,y.
    # This checks both compatibility and the exact transition probability.
    compatibility_pairs=0
    keys=list(permutations(range(3)))
    for n in range(1,5):
        words=list(product(range(3),repeat=n))
        for x in words:
            images=[tuple(key[a] for a in x) for key in keys]
            for y in words:
                count=sum(image==y for image in images)
                compatible=pattern(x)==pattern(y)
                assert (count>0)==compatible,(x,y,count)
                expected=math.factorial(3-len(set(x))) if compatible else 0
                assert count==expected,(x,y,count,expected)
                compatibility_pairs+=1
    rows=[]
    for n in range(1,4):
        for m in range(1,4):
            value,num=exact(n,m)
            rows.append({'N':n,'M':m,'numerator':value.numerator,'denominator':value.denominator,'weighted_good':num})
    source=r'''
#define main experiment_original_main
#include "EXPERIMENT_SOURCE"
#undef main
#include <cassert>
int main(){
  for(int n=1;n<=3;n++){
    int nw=1;for(int i=0;i<n;i++)nw*=3;
    vector<Record>w;vector<uint64_t>wt;
    for(int j=0;j<nw;j++){
      int a=j;uint8_t x[3]={};uint64_t weight=1;
      for(int i=n-1;i>=0;i--){x[i]=a%3;a/=3;weight*=x[i]+1;}
      w.push_back(encode(x,n));wt.push_back(weight);
    }
    for(int m=1;m<=3;m++){
      int nb=1;for(int i=0;i<m;i++)nb*=nw;
      uint64_t total=0;
      for(int b=0;b<nb;b++){
        int a=b;uint64_t weight=1;vector<Record>r;
        for(int i=0;i<m;i++){int j=a%nw;a/=nw;r.push_back(w[j]);weight*=wt[j];}
        auto st=statistics(r,n,false);
        total+=st.singleton*weight;
      }
      cout<<n<<" "<<m<<" "<<total<<"\n";
    }
  }
  uint8_t a[24]={},b[24]={};b[23]=1;
  auto x=encode(a,24),y=encode(b,24);
  assert(x.w!=y.w && x.p!=y.p && distinct(x.p,24)==1 && distinct(y.p,24)==2);
  b[0]=1;b[23]=0;auto z=encode(b,24);assert(z.w!=y.w && z.p!=y.p);
}
'''.replace('EXPERIMENT_SOURCE',str(ROOT/'scripts'/'experiment.cpp'))
    with tempfile.TemporaryDirectory() as td:
        path=Path(td); (path/'check.cpp').write_text(source)
        subprocess.run(['g++','-std=c++17','-O2',str(path/'check.cpp'),'-o',str(path/'check')],check=True)
        lines=subprocess.check_output([str(path/'check')],text=True).splitlines()
    assert len(lines)==len(rows)
    for line,row in zip(lines,rows):
        n,m,num=map(int,line.split())
        assert (n,m,num)==(row['N'],row['M'],row['weighted_good']),(line,row)
    # Check the occupancy recurrence independently against all uniform words.
    for n in range(1,5):
        g=3; a=[Fraction(1)]+[Fraction(0)]*g
        for _ in range(n):
            nxt=[Fraction(0)]*(g+1)
            for d in range(g+1):
                nxt[d]+=a[d]*Fraction(d,g)
                if d<g:nxt[d+1]+=a[d]*Fraction(g-d,g)
            a=nxt
        for m in (1,2,3,10):
            v=sum(a[d]*(1-Fraction(math.factorial(g)//math.factorial(g-d)-1,g**n))**(m-1) for d in range(1,g+1))
            words=list(product(range(g),repeat=n))
            ptn={w:pattern(w) for w in words}
            direct=sum(Fraction(1,g**n)*(1-Fraction(sum(ptn[w]==ptn[z] and w!=z for z in words),g**n))**(m-1) for w in words)
            assert v==direct,(n,m,v,direct)
    result={'explicit_key_compatibility_pairs':compatibility_pairs,'uniform_occupancy_cases':16,'status':'passed' ,'description':'Exact rational formula = exhaustive iid ensemble = production C++ class accounting; packing checked at N=24','cases':rows}
    (ROOT/'data'/'verification.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))
if __name__=='__main__':main()
