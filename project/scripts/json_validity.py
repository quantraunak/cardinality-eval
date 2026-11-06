"""JSON validity as emitted, per level and per arm, with no repair.

    python3 scripts/json_validity.py

The constrained arm is grammar-guaranteed to validate; the unconstrained arm is
prompted for JSON and validity is whatever the model produced. Recorded output
lives in paper/json_validity.txt. Added 2026-10-07 after the quote-repair fix
showed that invalid-as-emitted responses had been scored as zero recall.
"""
from __future__ import annotations

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from score_decoding import ARMS, score


def main() -> None:
    frames = {arm: score(directory, loose) for arm, (directory, loose) in ARMS.items()}
    common = sorted(set(frames["constrained"].doc_id) & set(frames["unconstrained"].doc_id))
    print(f"documents paired: {len(common)}\n")
    print(f"{'k':>4} {'constrained valid':>18} {'unconstrained valid':>20} {'unconstrained invalid, links recovered by repair':>48}")
    for k in sorted(frames["constrained"].k.unique()):
        c = frames["constrained"].set_index("doc_id").loc[common]
        u = frames["unconstrained"].set_index("doc_id").loc[common]
        cm, um = c[c.k == k], u[u.k == k]
        recovered = int(um[~um.valid].emitted.sum())
        print(f"{k:>4} {int(cm.valid.sum()):>12}/{len(cm):<5} {int(um.valid.sum()):>14}/{len(um):<5} {recovered:>48}")
    u = frames["unconstrained"].set_index("doc_id").loc[common]
    bad = u[~u.valid]
    print(f"\nunconstrained responses invalid as emitted: {len(bad)} of {len(u)}; "
          f"they carry {int(bad.emitted.sum())} links, {int(bad.tp.sum())} matching gold, "
          f"all scored as zero before the 2026-10-07 repair.")


if __name__ == "__main__":
    main()
