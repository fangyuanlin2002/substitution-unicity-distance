from pathlib import Path
import csv,json,numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
r=Path(__file__).resolve().parents[1]
obs={int(x['n']):x for x in csv.DictReader((r/'census_summary.csv').open())}
ns=[10,12,14,15,16,17,18,19,20]
ens={}
for order in [-1,0,1,2]:
 for n in ns:
  a=[list(map(float,p.read_text().strip().split(','))) for p in sorted((r/'results').glob(f'ensemble_{order}_{n}_*.csv'))]
  assert len(a)==3,(order,n,len(a))
  ens[order,n]=np.array(a)
f={}
for n in ns:
 p=r/'results'/f'precision_2_{n}.csv'
 if not p.exists():p=r/'results'/f'formula_2_{n}_20261119.csv'
 f[n]=list(map(float,p.read_text().strip().split(',')))
rows=[]
for n in ns:
 rows.append(dict(n=n,M=int(obs[n]['M']),actual=float(obs[n]['unique_probability']),uniform_RC=ens[-1,n][:,4].mean(),iid_RC=ens[0,n][:,4].mean(),one_context_RC=ens[1,n][:,4].mean(),two_context_RC=ens[2,n][:,4].mean(),formula=f[n][6],formula_se=f[n][7],threshold=f[n][8],particles=int(f[n][5])))
with (r/'results/comparison.csv').open('w') as out:
 w=csv.DictWriter(out,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
plt.rcParams.update({'font.family':'serif','font.size':10,'axes.spines.top':False,'axes.spines.right':False,'pdf.fonttype':42})
a=np.array([x['actual'] for x in rows]);fig,ax=plt.subplots(figsize=(6.3,3.6))
for k,label,style in [('uniform_RC','Uniform letters',':'),('iid_RC','English monograms','--'),('one_context_RC','One-letter context','-.'),('two_context_RC','Two-letter context','-')]:ax.plot(ns,[x[k] for x in rows],style,label=label,lw=1.6)
ax.plot(ns,a,'ko-',label='Actual corpus',lw=1.5,ms=4)
ax.axhline(.99,color='.65',lw=.7);ax.set(xlabel='Plaintext length (letters)',ylabel='Probability of unique recovery',ylim=(-.02,1.03),xticks=[10,12,14,16,18,20]);ax.legend(frameon=False,fontsize=9,loc='upper left');fig.tight_layout();fig.savefig(r/'figures/models.pdf');plt.close(fig)
fig,ax=plt.subplots(figsize=(6.3,3.6));v=np.array([f[n][6] for n in ns]);se=np.array([f[n][7] for n in ns]);ax.fill_between(ns,np.maximum(0,v-2*se),np.minimum(1,v+2*se),color='C0',alpha=.15,label='Formula: ±2 Monte Carlo SE')
ax.plot(ns,v,'C0-',label='Random-coding formula');ax.plot(ns,[x['two_context_RC'] for x in rows],'C1x',label='Whole-codebook check',ms=6);ax.plot(ns,[f[n][8] for n in ns],'C2--',label='Information-density threshold');ax.plot(ns,a,'ko-',label='Actual corpus',ms=4,lw=1.2);ax.axhline(.99,color='.65',lw=.7);ax.set(xlabel='Plaintext length (letters)',ylabel='Probability of unique recovery',ylim=(-.02,1.03),xticks=[10,12,14,16,18,20]);ax.legend(frameon=False,fontsize=8.5,loc='upper left');fig.tight_layout();fig.savefig(r/'figures/formula.pdf');plt.close(fig)
maxerr=max(abs(x['two_context_RC']-x['actual']) for x in rows)*100
maxformula=max(abs(x['formula']-x['actual']) for x in rows)*100
maxrange=max(np.ptp(ens[2,n][:,4]) for n in ns)*100
changes=[]
for n in [12,14,16]:
 low=list(map(float,(r/'results'/f'formula_2_{n}_20261119.csv').read_text().split(',')))
 changes.append(abs(f[n][6]-low[6])*100)
text=r'''We evaluated lengths $N\in\{10,12,14,15,16,17,18,19,20\}$. For each of the four source models and each length, we generated three independent codebooks of size $M_N$. Their mean uniquely recoverable message fraction evaluates the random-coding expectation by whole-codebook Monte Carlo. Figure~\ref{fig:models} compares these model predictions with the exact corpus census.
\begin{figure}[htbp]
\centering\includegraphics[width=\textwidth]{figures/models.pdf}
\caption{Random-coding predictions from public language statistics. Each model curve is the mean of three independent generated codebooks at each length. The black curve is the exact uniqueness probability in the fixed six-novel corpus.}\label{fig:models}
\end{figure}
'''
text+=f'The two-letter-context ensemble curve differs from the observed corpus curve by at most ${maxerr:.2f}$ percentage points over these tested lengths. The largest range across its three codebook replicates at any length is ${maxrange:.3f}$ percentage points. This replicate range describes numerical variation; it is not a confidence bound for model error.\n\n'
text+=r'''We also evaluated the formula directly using $3{,}000$ independently generated plaintexts per length and $2{,}000$ importance-sampling paths per plaintext. A precision check increased the latter count to $20{,}000$ at $N=12,14,16$, retaining the same outer plaintexts. The higher-particle results are used at those lengths in Figure~\ref{fig:formula} and Table~\ref{tab:results}.
'''
text+=f'The largest change in the estimated probability in this check was ${max(changes):.2f}$ percentage points. The largest outer Monte Carlo standard error of the displayed estimates is ${max(f[n][7] for n in ns)*100:.2f}$ percentage points. The standard errors include variation in the computed integrand but do not bound nonlinear importance-sampling bias. The whole-codebook calculation provides a separate numerical check on the ensemble prediction.\n\n'
text+=r'''\begin{figure}[htbp]
\centering\includegraphics[width=\textwidth]{figures/formula.pdf}
\caption{Two-letter-context model: direct numerical evaluation of the random-coding formula, its whole-codebook check, the information-density threshold approximation, and actual corpus uniqueness. The band is two estimated Monte Carlo standard errors, not a bound on model error or numerical bias.}\label{fig:formula}
\end{figure}
\begin{table}[htbp]\centering
\begin{tabular}{r|rrrr}
$N$ & Actual & Formula & Codebook check & Threshold\\\hline
'''
for x in rows:
 if x['n']>=14:text+=f"{x['n']} & {100*x['actual']:.2f} & {100*x['formula']:.2f} & {100*x['two_context_RC']:.2f} & {100*x['threshold']:.2f} \\\\\n"
text+=r'''\end{tabular}
\caption{Unique-recovery probabilities in percent. Formula and threshold use the public two-letter-context model; the codebook check averages three independent ensembles. Values printed as $100.00$ are rounded.}\label{tab:results}
\end{table}
'''
text+=f'The direct formula estimates are within ${maxformula:.2f}$ percentage points of the observed probabilities at the tested lengths. The threshold approximation changes too abruptly and is noticeably more optimistic through much of the transition. Thus replacing the full random-coding formula by a threshold on information density loses relevant finite-length behavior.\n\n'
x=next(x for x in rows if x['n']==18)
text+=f"At $N=18$, the actual uniqueness probability is ${100*x['actual']:.2f}\\%$, the directly evaluated formula gives ${100*x['formula']:.2f}\\%$, and the whole-codebook estimate gives ${100*x['two_context_RC']:.2f}\\%$. Both the actual curve and the two-letter-context random-coding curve first exceed $99\\%$ at $18$ among the tested lengths. In the supplied encryption experiment, $19{{,}}857$ of $20{{,}}000$ trials at this length gave unique recovery. These three comparisons have different roles: actual trials check the census, generated codebooks check the formula computation, and agreement between the formula and the real corpus assesses the model.\n\n"
text+=f"Absolute success-probability errors can obscure the failure tail. At $N=18$, the actual ambiguity rate is ${100*(1-x['actual']):.3f}\\%$, compared with ${100*(1-x['two_context_RC']):.3f}\\%$ under the ensemble calculation. The model therefore understates residual ambiguity despite locating the $99\\%$ crossing. No numerical claim here establishes a universal English threshold.\n"
(r/'results/results_text.tex').write_text(text)
print(dict(max_ensemble_error_pp=maxerr,max_formula_error_pp=maxformula,max_replicate_range_pp=maxrange,max_precision_change_pp=max(changes)))
