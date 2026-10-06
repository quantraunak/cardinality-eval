"""Interaction test: does the gap between arms change with k?

    python3 scripts/interaction_test.py

The pre-registered test is applied per arm and never tests the arm x k
interaction the paper's relative claim rests on. This script does, on the
cached responses, and also reports the k=1 under-emission that drives part of
the paired difference. See paper/interaction_test.txt for the recorded output.
"""
from __future__ import annotations

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(Path(__file__).resolve().parent))

import numpy as np
from scipy import stats
from score_decoding import ARMS, score


def ols_slope(x: np.ndarray, y: np.ndarray) -> tuple[float, float, float]:
    """Slope, its standard error and two-sided p, plain OLS with intercept."""
    res = stats.linregress(x, y)
    return res.slope, res.stderr, res.pvalue


def main() -> None:
    frames = {arm: score(directory, loose) for arm, (directory, loose) in ARMS.items()}
    common = sorted(set(frames["constrained"].doc_id) & set(frames["unconstrained"].doc_id))
    c = frames["constrained"].set_index("doc_id").loc[common]
    u = frames["unconstrained"].set_index("doc_id").loc[common]
    assert (c.k == u.k).all()
    k = c.k.to_numpy()
    diff = (u.recall - c.recall).to_numpy()

    print(f"documents paired: {len(common)}  (k levels {sorted(set(k))}, "
          f"{', '.join(f'k={kk}: n={int((k==kk).sum())}' for kk in sorted(set(k)))})\n")

    print("=== (a) interaction: OLS of paired difference (unconstrained - constrained) on log2 k ===")
    slope, se, p = ols_slope(np.log2(k), diff)
    print(f"  slope {slope:+.4f} per doubling of k   se {se:.4f}   p = {p:.4f}\n")

    print("=== (b) interaction: Spearman of paired difference against k ===")
    rho = stats.spearmanr(k, diff)
    print(f"  rho {rho.statistic:+.3f}   p = {rho.pvalue:.4f}\n")

    print("=== (c) unconstrained arm alone: Spearman of recall against k ===")
    for label, mask in (("k in {1,4,16}", k > 0), ("k in {4,16}", k >= 4)):
        r = stats.spearmanr(k[mask], u.recall.to_numpy()[mask])
        print(f"  {label:<14} n={int(mask.sum()):>3}  rho {r.statistic:+.3f}   p = {r.pvalue:.4f}")
    print()
    print("=== (c') constrained arm alone, same tests, for symmetry ===")
    for label, mask in (("k in {1,4,16}", k > 0), ("k in {4,16}", k >= 4)):
        r = stats.spearmanr(k[mask], c.recall.to_numpy()[mask])
        print(f"  {label:<14} n={int(mask.sum()):>3}  rho {r.statistic:+.3f}   p = {r.pvalue:.4f}")
    print()

    print("=== (d) empty link lists, per level ===")
    print(f"  {'k':>4} {'n':>4} {'constrained empty':>18} {'unconstrained empty':>20}")
    for kk in sorted(set(k)):
        m = k == kk
        print(f"  {kk:>4} {int(m.sum()):>4} {int((c.emitted[m] == 0).sum()):>18} "
              f"{int((u.emitted[m] == 0).sum()):>20}")
    print()

    print("=== (e) paired difference with k=1 empty-constrained documents excluded ===")
    keep = ~((k == 1) & (c.emitted.to_numpy() == 0))
    slope, se, p = ols_slope(np.log2(k[keep]), diff[keep])
    rho = stats.spearmanr(k[keep], diff[keep])
    print(f"  n={int(keep.sum())}  OLS slope {slope:+.4f} p = {p:.4f}   Spearman rho {rho.statistic:+.3f} p = {rho.pvalue:.4f}")
    print()

    print("=== (f) emitted items per document, by level ===")
    print(f"  {'k':>4} {'constrained':>12} {'unconstrained':>14}")
    for kk in sorted(set(k)):
        m = k == kk
        print(f"  {kk:>4} {c.emitted[m].mean():>12.2f} {u.emitted[m].mean():>14.2f}")


if __name__ == "__main__":
    main()
