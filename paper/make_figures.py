"""The two figures the paper needs. Both read the scored runs, nothing hardcoded."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "project"))
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "project" / "scripts"))

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from score_decoding import score, ARMS

plt.rcParams.update({"font.size": 9, "font.family": "serif", "axes.linewidth": 0.8,
                     "xtick.major.width": 0.8, "ytick.major.width": 0.8})

a = score(*ARMS["constrained"]).set_index("doc_id")
b = score(*ARMS["unconstrained"]).set_index("doc_id")
shared = a.index.intersection(b.index)
a, b = a.loc[shared], b.loc[shared]
ks = sorted(a.k.unique())

fig, ax = plt.subplots(1, 2, figsize=(7.0, 2.7))

# recall against k, both arms, with paired standard errors
for frame, label, style in ((a, "constrained", dict(color="#10657f", marker="o", ls="-")),
                            (b, "unconstrained", dict(color="#c2482c", marker="s", ls="--"))):
    m = [frame[frame.k == k].recall.mean() for k in ks]
    e = [frame[frame.k == k].recall.std(ddof=1) / np.sqrt((frame.k == k).sum()) for k in ks]
    ax[0].errorbar(range(len(ks)), m, yerr=e, capsize=2.5, lw=1.4, ms=4, label=label, **style)
ax[0].set_xticks(range(len(ks))); ax[0].set_xticklabels([f"$k$={k}" for k in ks])
ax[0].set_ylabel("recall"); ax[0].set_ylim(0.34, 0.72)
ax[0].legend(frameon=False, fontsize=8, loc="lower left")
ax[0].set_title("(a) recall against item count", fontsize=9)
ax[0].spines[["top", "right"]].set_visible(False)

# items emitted against items available
w = 0.36
for i, (frame, label, c) in enumerate(((a, "constrained", "#10657f"), (b, "unconstrained", "#c2482c"))):
    m = [frame[frame.k == k].emitted.mean() for k in ks]
    ax[1].bar(np.arange(len(ks)) + (i - 0.5) * w, m, w, label=label, color=c, alpha=0.85)
ax[1].plot(range(len(ks)), ks, "k:", lw=1.1, label="available")
ax[1].set_xticks(range(len(ks))); ax[1].set_xticklabels([f"$k$={k}" for k in ks])
ax[1].set_ylabel("items emitted"); ax[1].legend(frameon=False, fontsize=8)
ax[1].set_title("(b) emission against availability", fontsize=9)
ax[1].spines[["top", "right"]].set_visible(False)

fig.tight_layout()
fig.savefig(Path(__file__).parent / "figures" / "cardinality.pdf", bbox_inches="tight")
print("wrote figures/cardinality.pdf")
