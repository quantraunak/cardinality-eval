# Cardinality in Structured Extraction

> **Claim.** At pilot scale, neither decoding regime meets the pre-registered rejection rule for recall declining with the number of items (unconstrained: −0.131, p = 0.027, below the 0.15 the rule requires; constrained: recall rises, p = 0.73). What a grammar demonstrably buys at high item counts is validity: free-form responses stop being valid JSON as the list lengthens (25/25, 23/25, 21/25) while constrained ones never do (75/75).
> **Evidence.** `python3 project/scripts/score_decoding.py` and `python3 project/scripts/interaction_test.py` over the 150 cached responses in `project/data/processed/decoding_runs/` (outputs: `project/reports/decoding_result.txt`, `paper/interaction_test.txt`).
> **Pre-registered.** The hypothesis and the rejection rule (2026-09-10). Not pre-registered: the decoding factor (adopted 2026-09-11 after the think factor proved inert), the paired comparison, and the interaction test (2026-10-05). The k=1 gate (added 2026-09-10 after the first pilot failed) was never met.
> **Status.** One model, 25 documents per level. Corrected 2026-10-07: six unconstrained responses had been scored as zero links because the tolerant parser rejected unescaped quotes copied from the filings; the scorer now repairs them, and the earlier "0.214 drop, rejects" headline is withdrawn. Unrun: the `minItems` manipulation, a second model family, n ≥ 100 per level. Every number below traces to a line in `docs/CLAIMS.md`.

**Under the pre-registered rule, neither decoding regime rejects the null. Unconstrained
recall falls 0.131 from k=1 to k=16 (Spearman −0.255, p = 0.027; the rule needs a drop of
0.15 and p < 0.05) and schema-constrained recall does not fall (−0.114, i.e. it rises;
p = 0.73). The gap between arms moves −0.061 per doubling of k (p = 0.020), but that
interaction is carried by k=1, where the constrained arm returns an empty list on 13 of
25 documents; with those documents removed it vanishes (p = 0.17). What the grammar buys
with an artifact is validity: 25/25, 23/25, 21/25 unconstrained responses are valid JSON
as emitted, against 75/75 constrained. The study's own k=1 validity gate (recall ≥ 0.80)
was never met, so absolute levels are not interpretable. An earlier headline here (a
0.214 drop and a rejection) was a scorer defect, corrected 2026-10-07.**

## Objective

Position and context length are measured everywhere in the long-context literature, and
[multi-needle NIAH](https://www.langchain.com/blog/multi-needle-in-a-haystack) already
reports that retrieval falls as needle count rises. What is not measured is the same axis
for **structured extraction under constrained decoding**, with input length held constant
and the answer reported as a slope rather than an existence claim.

## Hypothesis

Pre-registered in [`docs/HYPOTHESIS_CARDINALITY.md`](docs/HYPOTHESIS_CARDINALITY.md),
a dated and amended document: recall declines in `k`, the number of items to emit, holding
schema and input length fixed. Rejection required **both** a drop of at least 0.15 from
`k<=3` to `k>=16` **and** p < 0.05. That hypothesis and rule were fixed before any cell
ran and did not change. The second factor did: the original design was model size ×
think/no-think, and on 2026-09-11 the think factor proved inert (identical `eval_count`
either way) and was replaced by constrained vs unconstrained decoding, which the
literature review had already named as the strongest competing explanation. The decoding
comparison was therefore adopted after the first cells ran, before the unconstrained arm
was run. The interaction test below was not pre-specified. The repository's first commit
(2026-09-14) contains both the pre-registration and the results, so the ordering rests on
the document's own dated amendments, not on commit history.

## Result

`qwen3:14b`, `num_ctx` 32,768, the same 75 documents in both arms (25 per level at
k ∈ {1, 4, 16}), drawn from the 300-document constructed set below. No response reached
the 24,000-token generation ceiling: the longest cached response is 903 tokens
(constrained) and 642 (unconstrained); the mean at k=16 is 686 constrained and 486
unconstrained. The cache does not record a stop reason, so "no truncation" is inferred
from that margin. The constrained
arm is parsed with the strict schema parser; the unconstrained arm with a tolerant parser
that strips reasoning, scans for the last balanced object and, since 2026-10-07, escapes
unescaped quotation marks inside string values and re-parses (`repair_quotes`, failing
closed). Before that repair, six complete responses carrying 39 links (38 matching gold)
were scored as zero because the model had copied a filing's short form verbatim, e.g.
`Express Scripts, Inc. ("Express Scripts")`.

**The k=1 validity gate was not met.** The pre-registration required recall ≥ 0.80 at k=1
for any slope to be interpretable, and said the constructed design would be abandoned if
the gate failed after one more rebuild. Final k=1 recall is 0.440 constrained and 0.640
unconstrained. The study proceeded anyway. Absolute recall levels below are therefore not
properties of the extractor; only the between-arm contrast on identical documents is read.

| k | constrained | unconstrained | paired diff | paired-t p | valid JSON (unc.) |
|---|---|---|---|---|---|
| 1 | 0.440 | 0.640 | +0.200 | 0.096 | 25/25 |
| 4 | 0.640 | 0.580 | −0.060 | 0.185 | 23/25 |
| 16 | 0.554 | 0.509 | −0.045 | 0.026 | 21/25 |

| arm | drop `k<=3` → `k>=16` | Spearman | pre-registered verdict |
|---|---|---|---|
| constrained | **−0.114** (recall rises) | +0.041, p = 0.73 | no effect |
| unconstrained | **+0.131** | −0.255, p = 0.027 | **does not reject** (drop < 0.15) |

Constrained responses are valid JSON 75/75 by construction.

**Interaction test** (added post hoc, `scripts/interaction_test.py`, output in
`paper/interaction_test.txt`). The per-arm verdicts above never test the claim that the
slopes differ. Regressing the paired difference (unconstrained − constrained) on log₂k:
slope −0.061 per doubling, p = 0.020; Spearman −0.291, p = 0.011. But at k=1 the
constrained arm returns an empty list on 13 of 25 documents (unconstrained: 8 of 25), and
those documents carry the interaction: without them the slope is +0.027 (p = 0.17). Within
each arm from k=4 to k=16, recall falls 0.580 → 0.509 unconstrained (Spearman −0.233,
p = 0.10) and 0.640 → 0.554 constrained (−0.237, p = 0.10). Above k=1 the arms decline
together. The between-arm recall difference rests entirely on the least reliable level
and is not a finding.

**Emission counts, not a mechanism.** At k=16 the constrained arm emits 9.4 items of 16
available and the unconstrained arm 8.5, at nearly identical precision (0.946 vs 0.953).
Both arms stop well short of 16; most of the larger gap reported earlier was the parser
defect. An earlier version of this
README said a half-filled array will not parse under the schema; that is false. The schema
is a bare `list[Link]` with no `minItems`, so the grammar allows closing the array after
any element, and the constrained arm does stop early and emits empty lists at k=1. The
manipulation that would test a grammar-level stopping account (`minItems`, or a required
count field) has not been run.

Unconstrained decoding costs **1.1× the tokens at k=1 and 0.7× at k=16**, and one
response in five at k=16 is not valid JSON as emitted.

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
as filler grows from 1,500 to 14,000 characters (recorded in
[`docs/HYPOTHESIS_CARDINALITY.md`](docs/HYPOTHESIS_CARDINALITY.md), 2026-09-10; the run
output itself was not committed). Reporting both arms brackets the true effect; reporting one and
not naming the choice does not.

## Data and models

| | |
|---|---|
| **Documents** | 300 constructed, `k` ∈ {1,2,4,8,16}, 60 per level, 9,000 chars each (`cardinality_docs.json`; `k_actual` equals `k_intended` for every document). The decoding comparison uses 75 of them: 25 at each of k ∈ {1, 4, 16} |
| **Item bank** | 143 verbatim-validated SEC filing sentences, each carrying exactly one named counterparty, screened empirically by whether the extractor recovers them at k=1 (`cardinality_bank_screened.parquet`). The number of candidates screened was not retained in a committed artifact |
| **Filler** | Relationship-dense sentences from the same corpus with every capitalised-run sentence removed |
| **Gold** | The injected set. `k` is exact by construction; no annotation |
| **Model** | `qwen3:14b` (dense), ollama, temperature 0, `num_ctx` 32768, `num_predict` 24000 |
| **Also run** | `qwen3:30b-a3b` constrained on all 300 documents (cells A, C, D in `cardinality_runs/`, retained but not used for any reported number) and `qwen3:30b-a3b` unconstrained (`decoding_runs/qwen3_30b-a3b_unconstrained`, discarded as context-bound; see the 2026-09-14 amendment) |
| **Committed** | Evaluation set, screened bank, and all 450 raw model responses, so the result re-scores without a GPU |

## Limitations

One model, dense, one family, so nothing here separates architecture from decoding. The
item bank was screened with `qwen3:30b-a3b` and evaluated with `qwen3:14b`, so the bank is
not guaranteed recoverable by the evaluated extractor, which is one candidate cause of the
failed k=1 gate. Twenty-five documents per level is pilot scale; the next run needs ≥ 100
per level and more than one model family. The
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

Getting there took four builds of the instrument, each recorded in
[`docs/HYPOTHESIS_CARDINALITY.md`](docs/HYPOTHESIS_CARDINALITY.md). The `k=1` gate was
tested on each and never met: 0.333, 0.400 and 0.400 during construction, then 0.440
(constrained) and 0.640 (unconstrained) on the final rebuild. The diagnoses along the way
were an item bank filtered by syntax rather than by measurement and filler so inert it
cost 0.25 recall on its own; separately, a 30B unconstrained arm was discarded as
context-bound. The gate itself was added after the first failure, not before it, and the
pre-registration records it that way.

## Value

For anyone running an LLM behind a JSON schema — which is most production extraction — this
says the schema is not what costs recall at high item counts, and that what it buys with
evidence is output validity: without it, free-form responses increasingly break JSON by
quoting the source, and a scorer without a repair step reads that as lost recall. Whether
the schema also protects recall is not settled at 25 documents per level. For anyone evaluating extraction, it says a single F1 is not comparable across
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
