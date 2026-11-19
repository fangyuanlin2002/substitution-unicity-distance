from pathlib import Path
import subprocess,csv,concurrent.futures
r=Path(__file__).resolve().parents[1];counts={int(x['n']):int(x['M']) for x in csv.DictReader((r/'census_summary.csv').open())}
def run(n):
 out=r/'results'/f'precision_2_{n}.csv'
 args=[str(r/'code/formula'),str(r/'results/transitions.bin'),'2',str(n),str(counts[n]),'20261119','3000','20000']
 out.write_text(subprocess.check_output(args,text=True));print(n,flush=True)
with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:list(pool.map(run,[12,14,16]))
