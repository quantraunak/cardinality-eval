# Cardinality in Structured Extraction

**Extraction recall degrades with the number of items a model must emit — but only when
decoding is unconstrained. Free generation loses 0.214 recall from k=1 to k=16
(Spearman −0.293, p = 0.011). Under a JSON schema the same model on the same documents
loses nothing (−0.114, i.e. recall rises; p = 0.73). The grammar is not the cost. It is
the mitigation.**

## Objective

Position and context length are measured everywhere in the long-context literature, and
[multi-needle NIAH](https://www.langchain.com/blog/multi-needle-in-a-haystack) already
reports that retrieval falls as needle count rises. What is not measured is the same axis
for **structured extraction under constrained decoding**, with input length held constant
and the answer reported as a slope rather than an existence claim.

## Hypothesis

Pre-registered in [`docs/HYPOTHESIS_CARDINALITY.md`](docs/HYPOTHESIS_CARDINALITY.md)
before any cell was run: recall declines in `k`, the number of items to emit, holding
schema and input length fixed. Rejection required **both** a drop of at least 0.15 from
`k<=3` to `k>=16` **and** p < 0.05. The literature review recorded constrained decoding as
the strongest competing explanation — the worry being that the cost of staying inside a
grammar grows with array length, making any apparent effect a property of the decoder.

## Result

`qwen3:14b`, `num_ctx` 32,768, 75 matched documents per arm, zero truncations, max 686
tokens against a 24,000 ceiling.

| k | constrained | unconstrained | paired diff | p |
|---|---|---|---|---|
| 1 | 0.440 | 0.640 | +0.200 | 0.096 |
| 4 | 0.640 | 0.530 | −0.110 | 0.110 |
| 16 | 0.554 | 0.426 | **−0.128** | **0.005** |

| arm | drop `k<=3` → `k>=16` | Spearman | pre-registered verdict |
|---|---|---|---|
| constrained | **−0.114** (recall rises) | +0.041, p = 0.73 | no effect |
| unconstrained | **+0.214** | −0.293, p = 0.011 | **rejects the null** |

The competing explanation is not merely unsupported; it points the wrong way.

**Mechanism.** At k=16 the constrained arm emits 9.4 items of 16 available and the
unconstrained arm 7.2, at nearly identical precision (0.946 vs 0.948). Left to decide when
to stop, the model stops early, and stops earlier as the list lengthens. A schema removes
the choice: a half-filled array will not parse, so generation continues.

Unconstrained decoding costs **1.1× the tokens at k=1 and 0.7× at k=16** — it is not a
compute tradeoff, it is strictly worse at high k on this model.

## Framework proposed

**Cardinality-controlled evaluation.** Report extraction quality as a curve `R(k)`, not a
scalar. A single F1 over a benchmark whose `k` distribution is unstated is not comparable
across benchmarks, because it silently averages over a `k` mix. Three commitments come with
it: show `k` decorrelated from input length or covary it; estimate per-document, never from
bucket means; and if `R(k)` declines, test whether splitting the input recovers the items,
or the mechanism claim dies even when the measurement survives.

**The count–density–length trilemma.** These are mechanically linked — density = (count ×
span length) / total length — so every study of item count fixes two and inherits a
confound in the third:

| fixed | varies | residual confound |
|---|---|---|
| length + count (here) | density | density aids high `k`; the effect is a **lower bound** |
| density + count (multi-needle NIAH) | length | length suppresses high `k`; an **upper bound** |

Measured cost of the choice: dilution alone moves recall 0.667 → 0.417 at constant `k=1`
across a 10× filler range. Reporting both arms brackets the true effect; reporting one and
not naming the choice does not.

## Data and models

| | |
|---|---|
| **Documents** | 300 constructed, `k` ∈ {1,2,4,8,16}, 60 per level, 9,000 chars each |
| **Item bank** | 143 verbatim-validated SEC filing sentences, each carrying exactly one named counterparty, screened empirically by whether the extractor recovers them at k=1 |
| **Filler** | Relationship-dense sentences from the same corpus with every capitalised-run sentence removed |
| **Gold** | The injected set. `k` is exact by construction; no annotation |
| **Model** | `qwen3:14b` (dense), ollama, temperature 0, `num_ctx` 32768, `num_predict` 24000 |
| **Also run** | `qwen3:30b-a3b` constrained, n=300 — retained in `cardinality_runs/` |
| **Committed** | Evaluation set, screened bank, and all 450 raw model responses, so the result re-scores without a GPU |

## Limitations

One model, dense, one family, so nothing here separates architecture from decoding. The
reasoning-mode factor **does not exist on this stack** — `think` only relabels which
response field the same tokens arrive in, verified by identical `eval_count` — so this says
nothing about inference-time reasoning. The 30B MoE arm was discarded as context-bound
rather than measuring decoding. The k=1 comparison is underpowered by this study's own
arithmetic: per-document recall there is a coin flip, requiring 106 documents against the
25 run, so +0.200 at p = 0.096 is reported and not interpreted.

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

## Value

For anyone running an LLM behind a JSON schema — which is most production extraction — this
says the schema is buying recall at high item counts, not costing it, and quantifies how
much. For anyone evaluating extraction, it says a single F1 is not comparable across
benchmarks unless the `k` distribution is stated, and gives the trilemma that determines
whether your measured effect is an upper or a lower bound.

## Reproduce

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
