#!/usr/bin/env python3
"""
The Unofficial Guide — command line.

    python app.py index                  build the search index (do this first)
    python app.py ask "your question"    ask one question
    python app.py ask                    ask questions until you quit
    python app.py chunks                 print sample chunks      (Milestone 3)
    python app.py retrieve "question"    show distances, no answer (Milestone 4)
    python app.py corpora                list the available corpora

Every command takes --corpus NAME to work with a different corpus without
editing config.py.
"""

import argparse
import sys
import time

import config


def cmd_corpora(args):
    from corpus_info import list_corpora

    for name, blurb in list_corpora():
        marker = "*" if name == config.CORPUS else " "
        print(f"{marker} {name}")
        print(f"    {blurb}\n")
    print("* = current default, set in config.py (AI201_CORPUS in .env wins)")


def cmd_index(args):
    from ingest import load_documents, describe as describe_docs
    from chunker import split_documents, describe as describe_chunks
    from store import build_index

    corpus = args.corpus or config.CORPUS
    print(f"Corpus: {corpus}")

    started = time.time()

    documents = load_documents(corpus)
    print(f"  loaded   {describe_docs(documents)}")

    chunks = split_documents(documents)
    print(f"  chunked  {describe_chunks(chunks)}")

    print(f"  embedding {len(chunks)} chunks (first run downloads the model)...")
    count = build_index(chunks, corpus=corpus, variant=args.variant)

    elapsed = time.time() - started
    print(f"  stored   {count} chunks in {elapsed:.1f}s")
    print(f"\nReady. Try: python app.py ask \"your question here\"")


def cmd_chunks(args):
    """Milestone 3. Print chunks so you can read them and paste them."""
    from ingest import load_documents
    from chunker import split_documents

    chunks = split_documents(load_documents(args.corpus or config.CORPUS))

    step = max(len(chunks) // args.n, 1)
    sample = chunks[::step][: args.n]

    print(f"{len(chunks)} chunks total. Showing {len(sample)}, spread across the corpus.\n")
    print("Paste these into your README under Sample Chunks. The rubric asks")
    print("for the source file and the function that produced them — both are")
    print("printed for you below.\n")

    for i, chunk in enumerate(sample, 1):
        print("=" * 70)
        print(f"Chunk {i}  |  source: {chunk.source}  |  produced by: {chunk.produced_by}")
        print("=" * 70)
        print(chunk.text)
        print()

    print("For each one, ask: could someone answer a question using only this,")
    print("without reading what came before or after?")


def cmd_retrieve(args):
    """Milestone 4. Retrieval only, with distances, and no model call."""
    from store import search
    import gate

    results = search(
        args.question,
        top_k=args.top_k or config.TOP_K,
        corpus=args.corpus or config.CORPUS,
        variant=args.variant,
    )

    if not results:
        print("Nothing came back. Have you run `python app.py index`?")
        return

    print(f"\nQuestion: {args.question}\n")
    print(f"{'#':<3} {'distance':<10} {'source':<32} preview")
    print("-" * 100)
    for i, r in enumerate(results, 1):
        preview = r.text[:52].replace("\n", " ")
        print(f"{i:<3} {r.distance:<10.4f} {r.source:<32} {preview}...")

    decision = gate.check(results)
    print(f"\nGate: {decision.explanation}")
    print("\nLower is better. 0.3 is a close match, 0.9 is unrelated.")
    print("Milestone 4: run your five questions, then three questions your")
    print("documents clearly don't cover, and look for the gap between the")
    print("two groups. Your cutoff goes in that gap.")


def _ask_one(question, corpus, variant, top_k, threshold, show_distances=True):
    from store import search
    import gate
    from generate import answer_from_chunks

    results = search(question, top_k=top_k, corpus=corpus, variant=variant)
    decision = gate.check(results, threshold=threshold)

    if show_distances:
        best = f"{decision.best_distance:.3f}"
        print(f"  (best distance {best}, cutoff {decision.threshold})")

    if not decision.passed:
        print(f"\n{gate.REFUSAL}\n")
        return gate.REFUSAL

    answer = answer_from_chunks(question, results)
    sources = sorted({r.source for r in results})
    print(f"\n{answer}\n")
    print(f"Sources retrieved: {', '.join(sources)}\n")
    return answer


def cmd_ask(args):
    corpus = args.corpus or config.CORPUS
    import generate as gen

    try:
        if args.question:
            _ask_one(args.question, corpus, args.variant, args.top_k, args.threshold)
        else:
            print("Ask a question, or press Enter on an empty line to quit.\n")
            while True:
                try:
                    question = input("> ").strip()
                except (EOFError, KeyboardInterrupt):
                    print()
                    break
                if not question:
                    break
                _ask_one(question, corpus, args.variant, args.top_k, args.threshold)
    finally:
        print(gen.usage())


def build_parser():
    parser = argparse.ArgumentParser(
        prog="app.py",
        description="The Unofficial Guide",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument("--corpus", help="corpus folder name (see corpora/README.md)")
    parser.add_argument(
        "--variant",
        default="default",
        help="index variant, for holding two chunkings at once (week 2)",
    )

    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("corpora", help="list available corpora").set_defaults(func=cmd_corpora)

    p_index = sub.add_parser("index", help="build the search index")
    p_index.set_defaults(func=cmd_index)

    p_chunks = sub.add_parser("chunks", help="print sample chunks (Milestone 3)")
    p_chunks.add_argument("-n", type=int, default=5, help="how many to print")
    p_chunks.set_defaults(func=cmd_chunks)

    p_ret = sub.add_parser("retrieve", help="show distances only (Milestone 4)")
    p_ret.add_argument("question")
    p_ret.add_argument("--top-k", type=int)
    p_ret.set_defaults(func=cmd_retrieve)

    p_ask = sub.add_parser("ask", help="ask a question")
    p_ask.add_argument("question", nargs="?")
    p_ask.add_argument("--top-k", type=int)
    p_ask.add_argument("--threshold", type=float, help="override the gate cutoff")
    p_ask.set_defaults(func=cmd_ask)

    return parser


def main():
    args = build_parser().parse_args()
    try:
        args.func(args)
    except KeyboardInterrupt:
        print("\nStopped.")
        sys.exit(130)
    except Exception as exc:  # noqa: BLE001 — students read this, not a traceback
        print(f"\n{type(exc).__name__}: {exc}\n", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
