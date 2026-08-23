#!/usr/bin/env python3
"""
STAFF TOOL — calibrate the relevance threshold for each corpus.

Students don't run this. It exists because the published cutoff of 0.6 is only
meaningful if it actually sits in the gap between in-corpus and out-of-corpus
distances, and that has to be measured per corpus rather than assumed.

    python tools/calibrate.py                  # every corpus
    python tools/calibrate.py --corpus city_guides

For each corpus it indexes the documents, runs a set of questions the corpus
should answer and a set it clearly can't, and reports the two distributions
plus the widest gap between them.

Requires the real embedding model — it will download about 90 MB on first run.
Run this on a machine with access to Hugging Face.

⚠️ Re-run this whenever the chunker changes. Chunk size moves the distances.
"""

import argparse
import statistics
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import config  # noqa: E402
from ingest import load_documents  # noqa: E402
from chunker import split_documents  # noqa: E402
from store import build_index, search  # noqa: E402


# Questions each corpus should be able to answer, and questions from another
# world entirely. Keep both lists honest — an out-of-corpus question that is
# secretly adjacent to the material will muddy the gap.
PROBES = {
    "campus_life": {
        "in": [
            "How long is the wait at Kestrel Commons at lunchtime?",
            "What is laundry like in Morrow House?",
            "Is the housing lottery actually random?",
            "How much work is CS 210 Data Structures outside class?",
            "How does the printing quota work?",
            "Which dorm is cheapest?",
            "When can I change my meal plan?",
            "What are the library's hours during term?",
        ],
        "out": [
            "What is the capital of Mongolia?",
            "How do I change the oil in a diesel engine?",
            "Who won the 1994 World Cup?",
            "What is the boiling point of mercury?",
            "How do I make sourdough starter?",
        ],
    },
    "advice_threads": {
        "in": [
            "Is a bike worth it for commuting on campus?",
            "How much RAM do I need in a laptop for CS courses?",
            "When is the laundry room least busy?",
            "Which meal plan tier should I get?",
            "Do professors actually reply to email?",
            "What do people wish they'd known in first year?",
            "How do I handle a group project where someone disappears?",
        ],
        "out": [
            "What is the capital of Mongolia?",
            "How do I change the oil in a diesel engine?",
            "Who won the 1994 World Cup?",
            "What is the boiling point of mercury?",
            "How do I make sourdough starter?",
        ],
    },
    "city_guides": {
        "in": [
            "How do I get to Kestrelford by bus?",
            "When is the best time of year to visit Halden Bay?",
            "Where should I eat in Pellew Sands?",
            "Is there parking in Halden Bay?",
            "What is there to see in Brightwater?",
            "How difficult is the road into Corry Vale?",
            "Does the railway run on Sundays?",
            "Which town is easiest to get around with limited mobility?",
            "How often do the trams run in Marchwood?",
            "Does the road to Elder Ness flood?",
            "What is there to do in Thornby Wells in winter?",
            "Can you tour the watermill at Givens Mill?",
            "Which walking route is easiest underfoot?",
            "Where is the good food in Marchwood?",
        ],
        "out": [
            "What is the capital of Mongolia?",
            "How do I change the oil in a diesel engine?",
            "Who won the 1994 World Cup?",
            "What is the boiling point of mercury?",
            "How do I make sourdough starter?",
        ],
    },
}


def best_distances(questions, corpus):
    out = []
    for question in questions:
        results = search(question, top_k=config.TOP_K, corpus=corpus)
        out.append(min(r.distance for r in results) if results else 1.0)
    return out


def calibrate(corpus: str) -> dict:
    print(f"\n{'=' * 68}\n{corpus}\n{'=' * 68}")

    started = time.time()
    documents = load_documents(corpus)
    chunks = split_documents(documents)
    build_index(chunks, corpus=corpus)
    index_time = time.time() - started

    print(f"{len(documents)} documents -> {len(chunks)} chunks, "
          f"indexed in {index_time:.1f}s")

    probes = PROBES.get(corpus)
    if not probes:
        print("No probe questions defined for this corpus — skipping.")
        return {}

    inside = best_distances(probes["in"], corpus)
    outside = best_distances(probes["out"], corpus)

    print(f"\n  in-corpus   n={len(inside):<3} "
          f"min {min(inside):.3f}  median {statistics.median(inside):.3f}  "
          f"max {max(inside):.3f}")
    print(f"  out-corpus  n={len(outside):<3} "
          f"min {min(outside):.3f}  median {statistics.median(outside):.3f}  "
          f"max {max(outside):.3f}")

    gap_low, gap_high = max(inside), min(outside)
    separated = gap_low < gap_high

    print()
    if separated:
        suggested = round((gap_low + gap_high) / 2, 2)
        print(f"  ✓ Clean separation. Gap runs {gap_low:.3f} to {gap_high:.3f}.")
        print(f"    Suggested threshold: {suggested}")
        if not (gap_low < config.THRESHOLD < gap_high):
            print(f"    ⚠️  The shipped default of {config.THRESHOLD} is OUTSIDE "
                  f"that gap. Either change the default for this corpus or say "
                  f"so in corpora/README.md.")
        else:
            print(f"    The shipped default of {config.THRESHOLD} sits inside "
                  f"the gap. Good.")
    else:
        overlap = gap_low - gap_high
        print(f"  ✗ NO clean separation — the groups overlap by {overlap:.3f}.")
        print(f"    Worst in-corpus is {gap_low:.3f}, best out-of-corpus is "
              f"{gap_high:.3f}.")
        print(f"    Any single cutoff will get some questions wrong. Look at "
              f"which in-corpus question scored worst — it's usually one the "
              f"corpus genuinely covers badly, and worth fixing in the corpus "
              f"rather than in the threshold.")

    if index_time > 180:
        print(f"\n  ⚠️  Indexing took {index_time:.0f}s. Milestone 4 budgets 90 "
              f"minutes total and week 2 re-indexes the whole corpus. Consider "
              f"trimming this corpus.")

    return {
        "corpus": corpus,
        "documents": len(documents),
        "chunks": len(chunks),
        "index_seconds": round(index_time, 1),
        "in_max": round(max(inside), 3),
        "out_min": round(min(outside), 3),
        "separated": separated,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--corpus", help="just this one")
    args = parser.parse_args()

    names = [args.corpus] if args.corpus else list(PROBES)
    rows = [calibrate(name) for name in names]

    print(f"\n{'=' * 68}\nSummary\n{'=' * 68}")
    print(f"{'corpus':<18}{'docs':>6}{'chunks':>8}{'index s':>9}"
          f"{'in max':>9}{'out min':>9}  separated")
    for row in rows:
        if not row:
            continue
        print(f"{row['corpus']:<18}{row['documents']:>6}{row['chunks']:>8}"
              f"{row['index_seconds']:>9}{row['in_max']:>9}{row['out_min']:>9}"
              f"  {'yes' if row['separated'] else 'NO'}")
    print("\nRecord these numbers in starter_repos.md before the term.")


if __name__ == "__main__":
    main()
