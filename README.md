# Cardinality in structured extraction

**Recall degrades with the number of items a model must emit — but only when
decoding is unconstrained. A JSON schema holds it flat.**

Ask a model to pull every named counterparty out of a document. Does it get worse
at that as the number of counterparties grows, holding everything else fixed?

The question is older than it looks. Position and context length are measured
everywhere, and [multi-needle
NIAH](https://www.langchain.com/blog/multi-needle-in-a-haystack) already reports
that retrieval falls as needle count rises. What is not measured is the same axis
for **structured extraction under constrained decoding**, with input length held
constant, reported as a slope rather than an existence claim.

## Result

`qwen3:14b`, 32k context, 75 matched documents per arm, zero truncations.

| k | constrained | unconstrained | paired diff | p |
|---|---|---|---|---|
| 1 | 0.440 | 0.640 | +0.200 | 0.096 |
| 4 | 0.640 | 0.530 | −0.110 | 0.110 |
| 16 | 0.554 | 0.426 | **−0.128** | **0.005** |

The pre-registered test required a recall drop of at least 0.15 from `k<=3` to
`k>=16` **and** p < 0.05.

| arm | drop | Spearman | verdict |
|---|---|---|---|
| constrained | **−0.114** (recall rises) | +0.041, p=0.73 | no effect |
| unconstrained | **+0.214** | −0.293, p=0.011 | **rejects the null** |

This inverts the explanation the literature review flagged as most threatening.
The worry was that the cost of staying inside a grammar grows with array length,
making any apparent cardinality effect a property of the decoder. The grammar is
what holds recall flat; removing it produces the decline.

The mechanism is in the emission counts. At `k=16` the constrained arm emits 9.4
items and the unconstrained arm 7.2, of 16 available, at nearly identical
precision (0.946 vs 0.948). Free to choose when to stop, the model stops early,
and stops earlier as the list lengthens. A schema removes the choice: a
half-filled array will not parse, so generation continues.

## How `k` is known exactly

Documents are constructed, not annotated. Each is `k` verbatim-validated sentences
from real SEC filings — each carrying exactly one named counterparty — injected at
uniformly random positions into filler drawn from the same corpus with every
capitalised-run sentence stripped, then padded to a constant 9,000 characters.

Gold is the injected set, so `k` is exact and free, and input length is constant
by construction rather than merely uncorrelated.

Getting there took four rejected builds, each recorded in
[`docs/HYPOTHESIS_CARDINALITY.md`](docs/HYPOTHESIS_CARDINALITY.md): a `k=1` gate
that failed three times, an item bank filtered by syntax rather than by
measurement, filler so inert it cost 0.25 recall on its own, and an arm that was
context-bound rather than measuring decoding.

## The count-density-length trilemma

Count, density and length are mechanically linked: density = (count × span length)
/ total length. Fixing any two determines the third, so every study of item count
picks two and inherits a confound:

| fixed | varies | residual confound |
|---|---|---|
| length + count (here) | density | density aids high `k`; the effect is a **lower bound** |
| density + count (multi-needle NIAH) | length | length suppresses high `k`; an **upper bound** |

Measured cost of the choice: dilution alone moves recall 0.667 → 0.417 at constant
`k=1` across a 10× filler range.

## What this does not establish

One model, dense, one family. The reasoning-mode factor does not exist on this
stack — `think` only relabels which response field the same tokens arrive in,
verified by identical `eval_count` — so nothing here speaks to inference-time
reasoning. The 30B MoE arm was discarded as context-bound, so the architecture
comparison is unrun.

## Reproducing

```bash
make install
make docs     # build the evaluation set
make arms     # both decoding arms, needs ollama with qwen3:14b
make score
```

`project/src/graph` is a pinned copy of the extraction engine from
[`filing-links`](https://github.com/quantraunak/filing-links). It is vendored
rather than imported because it is the system under test: the results describe
that exact version.
