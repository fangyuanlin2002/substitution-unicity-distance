from pathlib import Path
import numpy as np,subprocess,json
r=Path(__file__).resolve().parents[1]
v=np.fromfile(r/'results/transitions.bin',dtype='<f8');p=v[:26];T=v[26:702].reshape(26,26)
Q=p[:,None]*T;eq=np.trace(Q);M=100
qs=np.full((26,26),1-eq);np.fill_diagonal(qs,eq)
truth=float(np.sum(Q*(1-qs+Q)**(M-1)))
cmd=[str(r/'code/formula'),str(r/'results/transitions.bin'),'2','2',str(M),'871234','20000','1000']
a=subprocess.check_output(cmd,text=True).strip().split(',');estimate=float(a[6]);se=float(a[7])
assert abs(estimate-truth)<5*se+1e-4,(truth,estimate,se)
assert np.allclose(T.sum(axis=1),1)
report=dict(N=2,M=M,exact_ensemble_probability=truth,formula_estimate=estimate,reported_MC_standard_error=se,passed=True)
(r/'results/small_check.json').write_text(json.dumps(report,indent=2));print(report)
