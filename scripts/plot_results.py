#!/usr/bin/env python3
"""Regenerate publication figures solely from saved census and simulation data."""
from pathlib import Path
import csv
import math
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator, FuncFormatter

ROOT = Path(__file__).resolve().parents[1]
FIG = ROOT / 'figures'
DATA = ROOT / 'data'
FIG.mkdir(exist_ok=True)
plt.rcParams.update({
    'font.family': 'DejaVu Sans', 'font.size': 10,
    'axes.titlesize': 11, 'axes.labelsize': 10,
    'xtick.labelsize': 9, 'ytick.labelsize': 9,
    'legend.fontsize': 8.6, 'axes.spines.top': False,
    'axes.spines.right': False, 'axes.linewidth': .7,
    'pdf.fonttype': 42, 'ps.fonttype': 42,
    'savefig.dpi': 200,
})

def read_csv(name):
    with (DATA / name).open() as f:
        return list(csv.DictReader(f))

def field(row, *names):
    for name in names:
        if name in row:
            return float(row[name])
    raise KeyError(f'Missing {names} in {list(row)}')

def uniform_probability(n, m):
    n,m = int(n),int(m)
    a = np.zeros(27)
    a[0] = 1
    for _ in range(n):
        nxt = np.zeros_like(a)
        for d in range(27):
            nxt[d] += a[d] * d / 26
            if d < 26:
                nxt[d + 1] += a[d] * (26-d) / 26
        a = nxt
    result = 0.0
    for d in range(1, min(n,26)+1):
        orbit = math.factorial(26) // math.factorial(26-d)
        q = (orbit - 1) / 26**n
        result += a[d] * math.exp((m-1)*math.log1p(-q))
    return result

def style(ax):
    ax.grid(axis='y', color='#dce1e6', lw=.6, zorder=0)
    ax.set_axisbelow(True)
    ax.xaxis.set_major_locator(MaxNLocator(integer=True, nbins=8))
    ax.set_xlabel('Ciphertext length $N$ (letters)')

def save(fig, stem):
    fig.savefig(FIG / (stem+'.pdf'), bbox_inches='tight')
    fig.savefig(FIG / (stem+'.png'), bbox_inches='tight')
    plt.close(fig)

def main():
    census = sorted(read_csv('census.csv'), key=lambda x: int(x['N']))
    parts=sorted(DATA.glob('sim_Q*_*.csv'))
    if parts:
        sims=[]
        for path in parts:
            sims.extend(read_csv(path.name))
        with (DATA / 'simulation.csv').open('w') as f:
            writer=csv.DictWriter(f,fieldnames=list(sims[0]))
            writer.writeheader(); writer.writerows(sims)
    else:
        sims = read_csv('simulation.csv')
    ns = np.array([int(r['N']) for r in census])
    ms = np.array([int(field(r,'M','M_N')) for r in census])
    actual = np.array([field(r,'unique','unique_fraction','unique_probability') for r in census])
    uniform = np.array([uniform_probability(n,m) for n,m in zip(ns,ms)])
    labels = {
        'Q0':'Monograms (single letters)',
        'Q1':'Bigrams (1 preceding letter)',
        'Q2':'Trigrams (2 preceding letters)',
        'Q3':'Quadgrams (3 preceding letters)',
    }
    colors = {'Q0':'#0072B2','Q1':'#D55E00','Q2':'#009E73','Q3':'#9A4FA0'}
    estimates = {}
    rows = []
    for model in labels:
        means, ses, reps = [], [], []
        for n in ns:
            values = np.array([field(r,'unique','unique_fraction','unique_probability') for r in sims
                               if int(r['N']) == n and r['model'] == model])
            if len(values) != 5:
                raise ValueError(f'Expected five complete replicates for {model}, N={n}; got {len(values)}')
            means.append(values.mean())
            ses.append(values.std(ddof=1)/math.sqrt(len(values)) if len(values)>1 else float('nan'))
            reps.append(len(values))
            rows.append({'N':int(n),'model':model,'mean':means[-1], 'se':ses[-1], 'replicates':len(values)})
        estimates[model] = np.array(means),np.array(ses)
    with (DATA / 'model_summary.csv').open('w') as f:
        writer=csv.DictWriter(f,fieldnames=['N','model','mean','se','replicates'])
        writer.writeheader(); writer.writerows(rows)
    with (DATA / 'uniform_exact.csv').open('w') as f:
        writer=csv.writer(f); writer.writerow(['N','M','unique'])
        writer.writerows(zip(ns,ms,uniform))

    figs_axes = [plt.subplots(figsize=(8.2,5.7)) for _ in range(2)]
    axs = [item[1] for item in figs_axes]
    handles = []
    for j,ax in enumerate(axs):
        for model in labels:
            mean,se = estimates[model]
            y = mean if j==0 else 1-mean
            ylo = np.maximum(0,y-2*se)
            yhi = np.minimum(1,y+2*se)
            if j:
                y = np.where(y>0,y,np.nan)
                ylo=np.where(ylo>0,ylo,np.nan)
                yhi=np.where(yhi>0,yhi,np.nan)
            h, = ax.plot(ns,100*y, color=colors[model], lw=2, ls={'Q0':'-','Q1':'--','Q2':'-.','Q3':':' }[model], marker={'Q0':'s','Q1':'^','Q2':'D','Q3':'v'}[model], ms=4, label=labels[model], zorder=3)
            ax.fill_between(ns,100*ylo,100*yhi,color=colors[model],alpha=.17,linewidth=0,zorder=2)
            if j==0: handles.append(h)
        u=uniform if j==0 else 1-uniform
        if j: u=np.where(u>0,u,np.nan)
        h_u,=ax.plot(ns,100*u,color='#7D8790',ls='--',lw=1.8,label='Uniform letters',zorder=2)
        a=actual if j==0 else 1-actual
        h_a,=ax.plot(ns,100*a,color='#17212B',lw=2.2,marker='o',ms=3.4,label='Six-novel census',zorder=4)
        style(ax)
        if j==0:
            ax.set_title('Recovery transition',loc='left',pad=10)
            ax.set_ylabel('Unique plaintext recovery (%)')
            ax.set_ylim(-2,102); ax.set_xlim(max(10,ns.min()),min(20,ns.max()))
            ax.axhline(99,color='#adb5bd',lw=.8,ls=':',zorder=1)
            ax.annotate('99%',(ns.min()+.15,99),xytext=(0,-11),textcoords='offset points',fontsize=8,color='#626c76')
        else:
            ax.set_title('Ambiguity after the transition',loc='left',pad=10)
            ax.set_ylabel('Ambiguous plaintexts (%) · log scale')
            ax.set_yscale('log'); ax.set_ylim(1e-5,100)
            ax.set_xlim(max(14,ns.min()),ns.max())
            ax.axhline(1,color='#adb5bd',lw=.8,ls=':',zorder=1)
            ax.yaxis.set_major_formatter(FuncFormatter(lambda v,p:f'{v:.5f}'.rstrip('0').rstrip('.') if v<1 else f'{v:g}'))
    for j,(fig,ax) in enumerate(figs_axes):
        ax.legend(loc='lower right' if j==0 else 'lower left', frameon=True, fontsize=10)
        fig.tight_layout()
        save(fig,'recovery' if j==0 else 'ambiguity')


if __name__=='__main__':
    main()
