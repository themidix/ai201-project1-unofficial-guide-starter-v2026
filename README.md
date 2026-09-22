# The Unofficial Guide - City Guides

<!-- Replace this line with your name and which corpus you picked. -->

> **This file is your submission.** Fill it in as you go — most sections get
> written during the milestone that produces them, not at the end.
>
> How the starter works, and every command you'll need, is in `RUNNING.md`.
> Leave that file alone.
>
> **Paste everything as text.** No screenshots, no video. A typed table gets
> full credit; a picture of the same table gets none.
>
> Delete these instruction blocks as you replace them. The `<!-- -->` comments
> are notes to you and don't show up when the page renders — you can leave them
> or remove them.

---

# Unit 1

## What This Does

I chose the city_guides corpus, which contains fourteen structured travel
guides about towns and the surrounding region. The system answers practical
questions about transportation, accessibility, food, seasons, walking, and
what to see. The documents are organized by headings such as Getting there,
Getting around, and When to go, so the retrieval results can be connected to a
specific town or regional topic.

## Chunking Strategy

**Chunk size:** 800 characters
**Overlap:** 120 characters

The starter uses 800-character chunks with 120 characters of overlap. The
city-guide documents are much longer than the other corpora, averaging about
2,068 characters, and their useful information is spread across labelled
sections. I chose these starter values for the baseline, but the sample output
shows that fixed character boundaries cut through headings, words, and
sentences. That is the problem I would address in Milestone 3 with a
heading-aware chunker.

## Sample Chunks

<!-- Five chunks, pasted as text. Label each one and name the file it came from
     AND the function that produced it — the grader checks your code against
     what you claim here.

     `python app.py chunks -n 5` prints all three for you. Copy them straight
     across.

     Milestone 3. -->

**Chunk 1** - source: `guide_accessibility.md#0` - produced by: `chunker.py::fallback_split`

```
# Getting around the region with limited mobility

An honest assessment rather than a promotional one. Some of these places are
difficult and it is better to know in advance.

## Straightforward

**Thornby Wells** is the easiest town in the region. It is flat, compact, and
everything is within three minutes of everything else. Parking is free for two
hours anywhere in town and the station is central. The pump room and gardens
are level throughout.

**Marchwood** has a modern tram network with level boarding on all four lines,
running every 8 minutes on weekdays. The city museum and covered market are
both step-free. The distances between districts are the main consideration.
```

**Chunk 2** - source: `guide_corry_vale.md#2` - produced by: `chunker.py::fallback_split`

```
## When to go

May to September. Outside those months the pub in the third village closes,
the farm shop reduces its hours, and several footpaths become genuinely boggy
rather than merely wet. The road is not gritted above the second village and
is impassable in snow.

## Practical notes

Cash is still useful at the market and in smaller places, though cards are
accepted almost everywhere now. Mobile coverage is good in the centre and
patchy on the outskirts.
```

**Chunk 3** - source: `guide_givens_mill.md#0` - produced by: `chunker.py::fallback_split`

```
# Givens Mill

Givens Mill is a village of 700 built around a working watermill that still
grinds flour commercially. It is the sort of place people visit for an
afternoon and then talk about for longer than the visit lasted.

## Getting there

No station and no bus on Sundays; four buses a day from Brightwater on
weekdays, taking 30 minutes. Driving is 20 minutes.
```

**Chunk 4** - source: `guide_kestrelford.md#3` - produced by: `chunker.py::fallback_split`

```
The nearest full hospital is in Brightwater; there is a minor injuries unit
locally with limited hours.
```

**Chunk 5** - source: `guide_regional_transport.md#1` - produced by: `chunker.py::fallback_split`

```
The Kestrelford service is hourly on weekdays, two-hourly on Saturdays, and
does not run on Sundays. The Halden Bay coast service runs four times daily
year-round.

## Driving

Roads are good between the towns and poor on the approaches to both Kestrelford
and Halden Bay. Parking is the constraint rather than driving.
```

## Sample Answer

<!-- One complete question and answer, pasted as text, with the source line
     visible. Milestone 4. -->

**Question:** How often do Marchwood trams run on weekdays?

```
Marchwood's four-line tram network runs every 8 minutes on weekdays.
Source: `guide_marchwood.md`.
```

**My relevance cutoff:** 0.6

<!-- The number you set in config.py, and how you got there.

     You ran five questions your corpus covers and the five in OUT_OF_SCOPE
     that it clearly doesn't, and wrote down the best distance for each. What
     did those two groups look like? Where was the gap? Put the actual numbers
     here — the table below wants all ten rows.

     Milestone 4. -->

| Question | In corpus? | Best distance |
|---|---|---:|
| How often do Marchwood trams run on weekdays? | Yes | 0.364 |
| When are the gardens at Thornby Wells best? | Yes | 0.386 |
| Which town is easiest for visitors with limited mobility? | Yes | 0.485 |
| How many weekday buses run from Brightwater to Givens Mill? | Yes | 0.331 |
| How long does the railway take from Brightwater to the regional hub? | Yes | 0.305 |
| What is the capital of Mongolia? | No | 0.887 |
| How do I change the oil in a diesel engine? | No | 0.897 |
| Who won the 1994 World Cup? | No | 0.903 |
| What is the recommended dosage of ibuprofen for a headache? | No | 0.829 |
| How do I write a for loop in Rust? | No | 0.853 |

## How I Used AI

<!-- Two specific moments. For each: what you asked for, what came back, and
     what you changed about it.

     "I asked Claude to write the chunking function from my notes. It ignored
     the overlap, so I added that myself" is the level of detail we're after.
     "I used AI to help me code" is not.

     Milestone 5. -->

**1.** I used AI to help interpret the starter's output and identify that the
city guides were structurally different from the short-post corpora. I kept
the observation that the documents are heading-based, but chose the corpus and
the questions myself.

**2.** I used AI to diagnose the macOS CoreML failure from the ONNX runtime and
confirm that Chroma supports an explicit CPU provider. I changed `store.py` to
use `CPUExecutionProvider`, then verified that all 51 chunks indexed and that
an end-to-end question succeeded.

<!-- ── Stretch features ─────────────────────────────────────────────────────
     Doing one? Say so here BEFORE you start. A feature this README never
     claims earns nothing.
     ───────────────────────────────────────────────────────────────────────── -->

---

# Unit 2

<!-- These sections get ADDED to what's already above. Don't delete or rewrite
     unit 1 — the point is that someone can see what you said before you knew
     how it went. -->

## Run Log — Before

<!-- Your five criteria, three runs each. `python run_eval.py --label before`
     runs the questions, puts the OUT_OF_SCOPE ones through the gate, and
     writes it all into results/ for you. Targets come from criteria.md; the
     verdict column is your call.

     Criterion 3 is measured in one deterministic pass rather than three, so
     the same number goes in all three run columns. That's correct, not lazy.

     Milestone 1. -->

| Criterion | Target | Run 1 | Run 2 | Run 3 | Verdict |
|---|---|---|---|---|---|
| 1. Retrieved chunk contains the answer | 4 of 5 |  |  |  |  |
| 2. Every answer names a source | 5 of 5 |  |  |  |  |
| 3. Gate stops out-of-corpus questions | 4 of 5 |  |  |  |  |
| 4. | | | | | |
| 5. | | | | | |

<!-- Underneath, paste the REAL output for each criterion from one of your
     runs — the actual text your system produced, not a description of it.
     Name the file and function that produced it. -->

## Verdicts

<!-- MET or MISSED for each of the five, against the target you wrote last
     unit — not a new one. Plus a sentence on how you decided. That sentence
     matters most where it was close.

     If your target said 4 of 5 and your runs came out 4, 3, 4, that's a MISS.
     The target has to hold, not show up occasionally.

     Milestone 2. -->

| # | Criterion | Verdict | How I decided |
|---|---|---|---|
| 1 |  |  |  |
| 2 |  |  |  |
| 3 |  |  |  |
| 4 |  |  |  |
| 5 |  |  |  |

## Diagnoses

<!-- For each miss: which stage caused it, and how. The stage alone isn't
     enough — you need the mechanism.

     Not a diagnosis: "Question 3 didn't work."
     A diagnosis:     "Question 3 asks about laundry costs. The answer is in
                       one sentence that got split across two chunks, so
                       neither chunk on its own contains it."

     The five stages: loading → chunking → embedding → retrieval → generation.

     Look for a pattern. If three misses all ask about numbers, that's one
     problem, not three.

     Missed nothing? Say so, then say honestly whether your targets were set
     low, and which one you'd tighten and to what.

     Milestone 3. -->

## The Improvement

**What I changed:**

**Why I picked it:**

<!-- Connect it to a specific diagnosis above in one sentence. If you can't,
     you picked a fix because it sounded impressive. -->

### Run Log — After

<!-- Same format, same five criteria, three runs each.
     `python run_eval.py --label after` -->

| Criterion | Target | Run 1 | Run 2 | Run 3 | Verdict |
|---|---|---|---|---|---|
| 1. Retrieved chunk contains the answer | 4 of 5 |  |  |  |  |
| 2. Every answer names a source | 5 of 5 |  |  |  |  |
| 3. Gate stops out-of-corpus questions | 4 of 5 |  |  |  |  |
| 4. | | | | | |
| 5. | | | | | |

**Did it help?**

<!-- Say plainly whether it did, and how you know. If it made things worse,
     say that — a change that backfired, honestly reported, earns full credit
     and is more interesting than one that worked. What matters is that you can
     tell.

     Milestone 4. -->

## What's Still Broken

<!-- For each criterion still missed after your fix: what you'd do about it,
     and why you stopped where you did.

     "I ran out of time" is fine if it's true. Pretending nothing is left is
     not.

     Milestone 5. -->

## What I'd Do Differently

<!-- Knowing what you know now — which of your five criteria would you write
     differently, and why?

     Milestone 5. -->
