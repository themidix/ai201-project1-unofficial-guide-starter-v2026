"""
Your test questions.

Milestone 2 asks you to write five questions your system should be able to
answer from your corpus, specific enough to have a right answer.

  ✗ "What are good dining halls?"          — no right answer
  ✓ "What do students say about wait times at Commons during lunch?"

Fill in `QUESTIONS` below. `expects` is a word or short phrase you'd expect a
correct answer to contain — you'll use it in week 2 when you build a scorer,
and having written it now means you decided what "correct" meant before you saw
any results.

`OUT_OF_SCOPE` holds three questions your documents clearly don't cover. You
need these in Milestone 4 to find where your relevance cutoff belongs, and
again in week 2 to test that the gate still refuses them.
"""

QUESTIONS = [
    # {"question": "...", "expects": "..."},
    {"question": "", "expects": ""},
    {"question": "", "expects": ""},
    {"question": "", "expects": ""},
    {"question": "", "expects": ""},
    {"question": "", "expects": ""},
]

# Questions from a different world entirely. Your gate should refuse all three.
OUT_OF_SCOPE = [
    "What is the capital of Mongolia?",
    "How do I change the oil in a diesel engine?",
    "Who won the 1994 World Cup?",
]


def answered() -> list[dict]:
    """The questions you've actually filled in."""
    return [q for q in QUESTIONS if q.get("question", "").strip()]
