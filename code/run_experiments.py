from pathlib import Path
import csv,subprocess,concurrent.futures,json
root=Path(__file__).resolve().parents[1]
counts={int(r['n']):int(r['M']) for r in csv.DictReader((root/'census_summary.csv').open())}
ns=[10,12,14,15,16,17,18,19,20]
jobs=[]
for n in ns:
 for order in [-1,0,1,2]:
  for rep in range(3):
   jobs.append(('ensemble',order,n,2026111900+rep))
for n in ns:jobs.append(('formula',2,n,20261119))
def run(job):
 kind,order,n,seed=job
 out=root/'results'/f'{kind}_{order}_{n}_{seed}.csv'
 if out.exists():return str(out.name)
 args=[str(root/'code'/kind),str(root/'results/transitions.bin'),str(order),str(n),str(counts[n]),str(seed)]
 if kind=='formula':args+=['3000','2000']
 r=subprocess.run(args,text=True,capture_output=True,check=True)
 out.write_text(r.stdout)
 return str(out.name)
with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:
 for name in pool.map(run,jobs):print(name,flush=True)
