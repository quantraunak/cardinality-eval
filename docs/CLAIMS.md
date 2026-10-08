# Claims ledger

Every number this project states, where it appears, the artifact it comes from, whether
it was pre-registered, and its status after the 2026-10-07 consistency pass. "HYP" is
`docs/HYPOTHESIS_CARDINALITY.md` (dated amendments); "DR" is
`project/reports/decoding_result.txt` (regenerate with `python3 project/scripts/score_decoding.py`);
"IT" is `paper/interaction_test.txt` (`python3 project/scripts/interaction_test.py`);
"JV" is `paper/json_validity.txt` (`python3 project/scripts/json_validity.py`);
"site" is the raunaksood repo (`app/work/cardinality/page.tsx`, the blog post
`app/writing/the-schema-is-not-the-cost/page.tsx`, `lib/content.ts`).

| claim | where it appears | artifact | pre-registered? | status |
|---|---|---|---|---|
| Unconstrained recall drops 0.131 from k≤3 to k≥16; Spearman −0.255, p = 0.027; **does not meet the rule** (drop < 0.15) | README Result; paper abstract, §5; HYP correction 2026-10-07; site page; blog; content.ts | DR (repaired scoring) | Rejection rule yes (HYP 2026-09-10 Estimator); applying it per decoding arm follows the 2026-09-11 amendment, so the arm comparison is exploratory relative to the original design | **CORRECTED 2026-10-07**: the earlier 0.214 / p = 0.011 / "rejects" was a scorer defect (six unconstrained responses with unescaped quotes scored as zero links); withdrawn everywhere, disclosed in paper, README, HYP, site |
| Six of 75 unconstrained responses invalid as emitted (0 at k=1, 2 at k=4, 4 at k=16), all complete `}]}` objects, 39 links, 38 matching gold, scored as zero before the repair | README; paper §4, §5; HYP correction 2026-10-07; site; blog | JV; `repair_quotes` + `tests/test_parse_loose.py` | — | consistent (new 2026-10-07) |
| Valid JSON as emitted: unconstrained 25/25, 23/25, 21/25; constrained 75/75 | README; paper §5 (Validity); site; blog; content.ts | JV; DR "valid JSON" column | exploratory (not pre-specified) | consistent (new 2026-10-07) |
| Constrained drop −0.114 (rises); Spearman +0.041, p = 0.73 | same | DR | same | consistent |
| Paired table: k=1 0.440/0.640/+0.200/p 0.096; k=4 0.640/0.580/−0.060/0.185; k=16 0.554/0.509/−0.045/0.026 | README; paper Table 1; HYP correction 2026-10-07; blog; site | DR + IT | post hoc (paired test not pre-specified) | **CORRECTED 2026-10-07** (was 0.530/−0.110/0.110 and 0.426/−0.128/0.005 before the repair; HYP keeps the old table with the dated correction above it) |
| Interaction slope −0.061 per doubling, se 0.026, p = 0.020; Spearman −0.291, p = 0.011 | README; paper §5; HYP corrections 2026-10-05 and 2026-10-07; site; blog | IT (a), (b) | post hoc, 2026-10-05 | **CORRECTED 2026-10-07** (was −0.082, p = 0.006; −0.403, p = 0.0003) |
| Constrained empty list on 13 of 25 at k=1; unconstrained 8 of 25 | README; paper; HYP correction; site; blog | IT (d) | post hoc | consistent |
| Without those 13: slope +0.027, p = 0.17; Spearman −0.034, p = 0.79 | README; paper; site; blog | IT (e) | post hoc | **CORRECTED 2026-10-07** (was +0.007, p = 0.79; −0.185, p = 0.15) |
| Within-arm k=4→16: unconstrained 0.580→0.509, ρ −0.233, p = 0.10; constrained 0.640→0.554, ρ −0.237, p = 0.10 | README; paper | IT (c), (c′) | post hoc | **CORRECTED 2026-10-07** (unconstrained was 0.530→0.426, ρ −0.242, p = 0.09) |
| Emitted at k=16: 9.4 vs 8.5; precision 0.946 vs 0.953 | README; paper; HYP correction 2026-10-07; site; blog | DR; IT (f) | exploratory | **CORRECTED 2026-10-07** (was 7.2 / 0.948; most of the earlier gap was the parser defect) |
| Paper title "What Constrained Decoding Buys at High Item Counts: Validity, Not Recall" (was "Cardinality Degradation in Structured Extraction: A Constructed-Document Pilot…", before that "Constrained Decoding Prevents Cardinality Degradation…") | paper; content.ts; site | — | — | retitled 2026-10-07 to claim only what has an artifact |
| Token cost ratio 1.1× at k=1, 0.7× at k=16 | README; paper; HYP; blog | DR | exploratory | consistent |
| "Maximum 686 tokens against a 24,000 ceiling" | README Result; paper §4; HYP Result 2026-09-14; blog ("zero truncations") | `decoding_runs/*.json` `eval_count`: mean at k=16 constrained 686; **maximum 903 constrained, 642 unconstrained** | — | **CONTRADICTION** (a mean reported as a maximum). Fixed in README and paper; dated correction added to HYP |
| Zero truncations | README; paper; HYP; blog | no stop reason in cache; inferred from 903 ≪ 24,000 | control 2, HYP 2026-09-10 | consistent, now stated as inferred |
| k=1 gate 0.80; failures 0.333, 0.400, 0.400; final 0.440 / 0.640; stop rule "no fourth iteration"; study proceeded anyway | README; paper §2, §4; HYP 2026-09-10 amendments; site; blog | HYP (record) + DR | gate added 2026-09-10 **after** the first pilot failed, recorded as such | README "four rejected builds / failed three times" was ambiguous: fixed. Site and blog said the gate was set before the first pilot: **CONTRADICTION** with HYP, fixed in the site PR |
| 75 documents, 25 per level, k ∈ {1, 4, 16}, same documents in both arms | README; paper; site; blog | `decoding_runs/` (75 files per arm; `k_actual` = `k_intended` for all) | 2026-09-11 amendment | consistent; README's "300 documents, 60 per level" is the constructed set and now says so |
| 300 constructed documents, 9,000 characters | README; paper | `cardinality_docs.json` (300; 8,993–8,999 chars) | length amended from 14,000 (HYP 2026-09-10) | consistent |
| "143 of 240 candidates survive" screening | paper §2; README (143) | `cardinality_bank_screened.parquet` = 143; no artifact for 240; HYP 2026-09-10 records 427 first-person spans before the rebuild | — | **UNTRACEABLE (240)**: removed from the paper, README marks the pre-screen count as not retained |
| Dilution: recall 0.667 / 0.583 / 0.417 at 1,500 / 4,000 / 14,000 filler characters; "0.25" | README ("10× range"); paper §2 table; HYP 2026-09-10; site; blog | HYP table only; run output not committed | measured 2026-09-10 | **UNTRACEABLE beyond the record**: marked in README and paper; "10×" replaced by the character range |
| 106 documents needed at k=1 for a 0.15 difference at 80% power | README; paper; HYP | arithmetic stated in HYP (Bernoulli variance) | — | consistent (derivation) |
| Think factor inert: identical `eval_count` (268 / 4,914) | README; paper §4; HYP 2026-09-11 | HYP table (one document) | — | consistent |
| 18× token ratio on the 30B MoE | HYP 2026-09-11; blog | HYP table; labelled an artifact of the 8,192 window in HYP 2026-09-14 and the blog | — | consistent |
| 30B unconstrained: 4 of 6 k=16 documents truncated; +0.033 / −0.014 withdrawn | HYP 2026-09-14; paper §4 | HYP; `decoding_runs/qwen3_30b-a3b_unconstrained` | — | consistent |
| "qwen3:30b-a3b constrained, n=300, retained" vs "the 30B arm was discarded" | README | `cardinality_runs/{A,C,D}` exist; the discarded arm is the 30B *unconstrained* run | — | **CONTRADICTION** (wording): fixed |
| README Value: "the schema is buying recall at high item counts … and quantifies how much" vs headline "whether it is the mitigation is not settled" | README | — | — | **CONTRADICTION**: Value section rewritten |
| Hypothesis and rejection rule fixed before any cell ran; decoding factor adopted 2026-09-11; interaction test not pre-specified; first commit 2026-09-14 holds both | README; paper §4 | HYP; `git log` | — | consistent |
| Paper Contributions: "the pre-registered decline is present under unconstrained decoding" | paper §1 | — | the decline *rule* was pre-registered; the decoding arm was not | **mislabel**: reworded |
| Blog: "Getting it to work took five attempts" | blog | HYP records three gate failures and one rebuild (four builds) plus a discarded 30B arm | — | **CONTRADICTION** with README/HYP: fixed in the site PR |
| content.ts: "failed its own sanity check three times during construction and never cleared it" | site | HYP + DR | — | consistent |
| Item bank screened with qwen3:30b-a3b, evaluated with qwen3:14b | README; paper §6 | HYP 2026-09-14 | — | consistent |

## What needs a new experiment, not an edit

- Whether either regime's recall declines with k at all under the rule: n ≥ 100 per level (the unconstrained drop is 0.131 against a 0.15 rule, and p = 0.027, so the pilot is underpowered for the size condition).
- Whether the schema protects recall above k=1 (the between-arm slope is carried by k=1): `minItems` / required-count manipulation, and n ≥ 100 per level.
- Whether the k=1 gate can be met at all with a bank screened by the evaluated model: re-screen the bank with `qwen3:14b`.
- A second model family.
- Re-running the dilution ladder and committing its output, so the 0.667 / 0.583 / 0.417 row has an artifact.
