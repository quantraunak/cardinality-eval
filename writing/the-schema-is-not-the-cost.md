# The schema is not the cost

If you run an LLM behind a JSON schema, you have probably worried about what the grammar is
doing to the model. Constrained decoding masks tokens the model wants, and the reported
costs are real: several percentage points of accuracy across open-weight models, and at
least one function-calling result where unconstrained generation with post-hoc parsing beat
constrained decoding outright.

I went looking for that cost in a specific place and found the opposite.

## The question

Ask a model to pull every named counterparty out of a 10-K. Does it get worse at that as
the number of counterparties grows, holding the document length and the schema fixed?

Call the number of items `k`. The question is whether recall declines in `k`.

It is not a new question in spirit. [Multi-needle
NIAH](https://www.langchain.com/blog/multi-needle-in-a-haystack) already reports that
retrieval falls as needle count rises, and the long-context literature measures position
and input length exhaustively. What nobody had measured, as far as I could find, was the
same axis for structured extraction under a grammar, with input length actually held
constant, reported as a slope rather than as "it declines."

And there was a specific reason to care. In my own extraction work I had written down
constrained decoding as the strongest competing explanation for any cardinality effect I
might find: if the cost of staying inside a grammar grows with the number of array
elements, then what looks like a model limitation is really a decoder artifact. I had
recorded that as unfalsified and moved on, which is a comfortable way to stay wrong.

## Building a ruler that works

You cannot answer this by annotating documents, because `k` is the treatment. If `k` comes
from whichever filings you happened to sample, and a human has to recover it, then it is
measured with error that correlates with the outcome, because an annotator's attention flags
on exactly the long enumerations where the effect should live.

So I built the documents instead. Take sentences from real filings, each one
verbatim-validated and carrying exactly one named company. Inject `k` of them at random
positions into filler drawn from the same corpus, with every sentence containing a
capitalised name stripped out. Pad everything to a constant length. Gold is the set you
injected, so `k` is exact and free.

That is the design. Getting it to work took five attempts, and the four failures are more
instructive than the design is.

I set a sanity gate first: at `k=1`, with one item in one document, recall must clear 0.80.
One needle, from a sentence the extractor itself produced in the wild.

**It came back 0.333.** Then, after a fix, 0.400. Then 0.400 again.

The first cause was that my injected sentences named *their own original filer* in the
third person ("BDS faces strong competition from Lockheed Martin") while the document was
attributed to a placeholder company. The model was being asked who ACME deals with and
correctly declining to say Lockheed. I restricted the bank to first-person sentences, which
transplant cleanly: "Wal-Mart accounted for 22 percent of our consolidated net sales" is
true of whoever files it.

Recall went to 0.400. Still broken.

The second round found four defects at once: an all-caps ticker in the filler that the
name-detector missed and the model kept emitting, paragraph chunking that sliced injected
sentences in half at fixed character offsets, gold items that were not company names at all
("One of our end customers"), and a matching rule strict enough to score `Komatsu` against
`Komatsu Cummins Chile, Ltda.` as a miss.

Fixed all four. Recall: 0.400.

At that point I stopped patching things I could see and ran a controlled comparison
instead: same sentence, same `k=1`, only the amount of filler varying.

| filler | recall |
|---|---|
| 1,500 chars | 0.667 |
| 4,000 chars | 0.583 |
| 14,000 chars | 0.417 |

**Dilution alone was worth 0.25 recall.** My documents were 99% deliberately inert text. I
had built the filler by selecting prose *for containing no company names*, which made it
far more inert than any real prompt, where a passage selector keeps only relationship-dense
paragraphs. The gate was never failing because of the bank or the chunking. It was failing
because I had buried one sentence in a haystack far emptier than anything the model sees in
practice.

It also exposed something structural. Count, density and length are mechanically linked:
density = (count × span length) / total length. Fix any two and the third follows. So every
study of item count picks two and inherits a confound in the third. Fix length and let
density rise with `k`, as I did, and high-`k` documents get a density advantage that
partially cancels the effect, so your measurement is a lower bound. Fix density and let
length grow, as multi-needle NIAH does, and length suppresses high `k`, giving an upper
bound. There is
no third option where all three hold.

The fifth build used shorter documents, shorter spans, and an item bank screened
empirically, keeping a sentence only if the extractor actually recovers it at `k=1`, rather
than by my guesses about which sentences transplant. Those guesses had been wrong three
times running.

## The result

`qwen3:14b`, 32k context, 75 matched documents per arm, zero truncations.

| k | constrained | unconstrained |
|---|---|---|
| 1 | 0.440 | 0.640 |
| 4 | 0.640 | 0.530 |
| 16 | 0.554 | **0.426** |

The pre-registered test required a recall drop of at least 0.15 from `k<=3` to `k>=16` and
p < 0.05, both fixed before any cell ran.

**Unconstrained decoding: drop +0.214, Spearman −0.293, p = 0.011.** Rejects.

**Constrained decoding: drop −0.114, meaning recall *rises*. Spearman +0.041, p = 0.73.**
Nothing.

Paired on the same documents, unconstrained leads by 0.200 at `k=1` and trails by 0.128 at
`k=16` (p = 0.005). The crossover is the effect.

So the cardinality effect is real, and the grammar is what prevents it.

## Why

The emission counts give it away. At `k=16` the constrained arm emits 9.4 items of the 16
available; the unconstrained arm emits 7.2. Precision is identical at 0.946 and 0.948, so
this is not a quality tradeoff. The unconstrained arm simply produces fewer items, and
produces relatively fewer as the list grows.

Left to decide when to stop, the model stops early. A schema takes that decision away,
because a half-filled array is not a valid parse, so generation continues.

That also kills a number I had believed earlier in the week. On a 30B mixture-of-experts
model, unconstrained generation cost 18× the tokens of constrained. I reported that as a
fact about removing the grammar. It was not. That model was writing 7,000 to 12,000 tokens
against an 8,192-token context window, so the arm was measuring a wall, not a decoder. On a
model whose generation fits, unconstrained costs 1.1× at `k=1` and **0.7× at `k=16`**. It is
cheaper and worse.

## What I would take from this

For anyone shipping structured extraction: the schema is not the thing costing you recall
at high item counts. It is the thing holding recall up. If you have been considering
free-form generation with post-hoc parsing to escape grammar masking, measure the item-count
axis before you switch, because on this model that trade goes the wrong way and costs
nothing in tokens to discover.

For anyone evaluating extraction: a single F1 over a benchmark whose `k` distribution is
unstated is not comparable to another benchmark's F1. You are averaging over a mix nobody
reported. And if you measure the axis, say which two of count, density and length you fixed,
because that choice determines whether your number is an upper or a lower bound.

The methodological lesson is narrower and more annoying. I had this tool's limitation
written down in my own test suite, in a test asserting it so it "cannot quietly stop being
true." I had recorded constrained decoding as the strongest competing explanation and left
it unfalsified. Writing down what you have not ruled out is not the same as ruling it out,
and the gap between those two things was, in this case, the entire finding.

Code, pre-registration, evaluation set and all 450 raw model responses:
[cardinality-eval](https://github.com/quantraunak/cardinality-eval). The result re-scores
without a GPU.
