"""Item-level recall slope, with and without item fixed effects (exploratory, added 2026-11-05).

    python3 scripts/item_fe.py

Documents draw items from a 97-item bank, so items recur across documents and k
levels. A document-level slope can reflect which items were drawn at each k rather
than k itself. This regresses per-item hit (0/1) on log2 k, standard errors
clustered by document, with and without one indicator per item.
"""
import sys, json, pathlib; HERE = pathlib.Path(__file__).resolve().parent; sys.path.insert(0, str(HERE.parent)); sys.path.insert(0, str(HERE))
import numpy as np, pandas as pd
from scipy import stats
from score_decoding import ARMS, DOCS
from run_decoding_arm import parse_loose
from src.graph import extract, resolve
from score_cardinality import _subsumes
rows=[]
for arm,(d,loose) in ARMS.items():
    for p in sorted(d.glob('*.json')):
        if p.stem not in DOCS: continue
        doc=DOCS[p.stem]; t=json.loads(p.read_text())['text']
        links=parse_loose(t) if loose else extract.parse_response(t)
        got={resolve.normalize(l['counterparty']) for l in links if l.get('counterparty')}
        for g in doc['gold']:
            w=resolve.normalize(g['counterparty'])
            hit=int(w in got or _subsumes(w,got-{w}))
            rows.append(dict(arm=arm,doc=p.stem,k=doc['k_actual'],item=w,hit=hit))
df=pd.DataFrame(rows); df['lk']=np.log2(df.k)
def clus(s,fe):
    X=[np.ones(len(s)),s.lk.values]
    if fe: X+= [ (s.item==i).astype(float).values for i in sorted(s.item.unique())[1:] ]
    X=np.column_stack(X); y=s.hit.values.astype(float)
    XtXi=np.linalg.pinv(X.T@X); b=XtXi@X.T@y; e=y-X@b
    g=pd.factorize(s.doc)[0]; M=np.zeros((X.shape[1],)*2)
    for c in np.unique(g):
        u=X[g==c].T@e[g==c]; M+=np.outer(u,u)
    V=XtXi@M@XtXi; G=len(np.unique(g)); se=np.sqrt(V[1,1]*G/(G-1))
    return b[1], 2*stats.t.sf(abs(b[1]/se),G-1)
for arm in ['unconstrained','constrained']:
    s=df[df.arm==arm]
    for fe in [False,True]: print(arm,'FE' if fe else 'noFE',[round(v,3) for v in clus(s,fe)])
k1=set(df[(df.k==1)].item); hi=df[(df.k>=4)&(df.arm=='unconstrained')]
print('k1 items',len(k1),'recall at k>=4: k1-items',round(hi[hi.item.isin(k1)].hit.mean(),3),'others',round(hi[~hi.item.isin(k1)].hit.mean(),3))
