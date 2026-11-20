#!/usr/bin/env python3
"""Rebuild the census, independent random-codebook simulations, and figures.

Snapshots are included; default execution needs no network. Run --plots-only to redraw
from supplied numerical outputs. Requires C++17, Python, NumPy, Matplotlib.
"""
from pathlib import Path
import argparse,subprocess,sys,concurrent.futures
ROOT=Path(__file__).resolve().parent
p=argparse.ArgumentParser();p.add_argument('--plots-only',action='store_true');p.add_argument('--workers',type=int,default=4);a=p.parse_args()
def run(cmd):subprocess.run(cmd,cwd=ROOT,check=True)
if not a.plots_only:
 run([sys.executable,'scripts/preprocess.py'])
 run(['g++','-O3','-std=c++17','scripts/experiment.cpp','-o','scripts/experiment'])
 run(['scripts/experiment',str(ROOT),'census'])
 def sim(job):
  q,r=job
  with (ROOT/'data'/f'sim_Q{q}_{r}.log').open('w') as f:
   subprocess.run([str(ROOT/'scripts'/'experiment'),str(ROOT),'sim',str(q),str(r)],stdout=f,stderr=f,check=True)
 with concurrent.futures.ThreadPoolExecutor(max_workers=a.workers) as ex:
  list(ex.map(sim,[(q,r) for q in range(4) for r in range(5)]))
run([sys.executable,'scripts/verify_small.py'])
run([sys.executable,'exact_example.py'])
run([sys.executable,'scripts/plot_results.py'])
