# Acceptance criteria — The Unofficial Guide

Five criteria that say what "working" means for this system, written in unit 1
**before** any results existed.

An acceptance criterion names a target: a number, a count, a rate, or something
a person could plainly observe. *"Retrieval works"* is an opinion. *"For at
least 4 of my 5 test questions, the top results include a chunk containing the
answer"* is a criterion.

Under each one, write a sentence or two on **why that target** and not a
stricter or looser one. A reason that says something about your corpus or your
pipeline earns credit; *"80% seemed reasonable"* does not.

> Missing your own targets next unit costs you nothing. Setting a target so
> easy you can't miss it does.

---

## 1. Retrieved chunks contain the answer

For at least 4 of my 5 test questions, the retrieved chunks include one that
contains the answer.

**Why this target:**
In `campus_life`, useful information typically sits in a single specific sentence within an individual short post (~317 characters average across 88 documents). I chose 4 of 5 (80%) rather than 5 of 5 because queries involving specific policies (like bookstore price-matching or reading week library hours) share keywords with related administrative and study posts, which could occasionally push the target chunk out of the top results under vector search.

---

## 2. Every answer names a source

Every answer the system produces names at least one source document.

**Why this target:**
This target is set to 5 of 5 (100%) because source attribution is structurally enforced by the system prompt (`GROUNDING_INSTRUCTION`), which mandates citing the exact source filename provided in each retrieved excerpt. Any generated response that omits a source citation indicates a failure of prompt adherence rather than a retrieval difficulty.

---

## 3. The relevance gate stops out-of-corpus questions

When I ask a question my documents clearly don't cover, the relevance gate
stops it and the system returns "I don't have enough information about that" —
in at least 4 of 5 tries.

**Why this target:**
The five test questions in `OUT_OF_SCOPE` cover distant domains like diesel engine maintenance, Mongolian geography, and Rust programming. In cosine distance space, completely unrelated queries reliably score above 0.65–0.75, cleanly separated from relevant campus life queries (which score between 0.20 and 0.45). Setting the target to 4 of 5 (80%) provides a realistic tolerance for accidental lexical overlap in vector representations while guaranteeing high-precision rejection.

---

## 4. Standalone chunk integrity

At least 4 of 5 sampled chunks contain a complete, standalone thought with no sentence severed mid-thought at either the beginning or end of the chunk.

**Why this target:**
`campus_life` posts are short (most are 1 to 3 paragraphs). The starter's fixed character-window chunker cuts text blindly at character offsets, frequently slicing sentences in half or separating a crucial conclusion from its premise. Measuring that at least 4 of 5 chunks preserve complete sentence boundaries ensures that retrieved context is coherent and directly answerable on its own.

> **Revised in unit 2:** For at least 4 of 5 test questions, the top-1 retrieved chunk is a complete, standalone passage that contains no truncated sentences at either start or end.
>
> **Why revised:** The original criterion specified "sampled chunks" without defining an explicit, repeatable sampling protocol during the three query runs executed by `run_eval.py`. Re-anchoring it to the top-1 retrieved chunk for each test query makes the measurement directly verifiable and linked to the actual query pipeline.

---

## 5. Ground-truth source attribution accuracy

For all 5 test questions, every cited source document in the final answer corresponds to the ground-truth document that actually contains the factual answer (no incorrect or distractor source attributions).

**Why this target:**
In a RAG pipeline with top-k retrieval, several distractor chunks are injected into the context window alongside the relevant passage. A system might cite any document in the context to look authoritative; requiring 5 of 5 cited documents to be the exact ground-truth source ensures attribution is truthful and verifiable, not superficial.



---

<!-- ─────────────────────────────────────────────────────────────────────────
     UNIT 2 — read this before you change anything above.

     If a criterion turns out to be BROKEN rather than merely unmet, you can
     revise it, and that earns credit. But never delete or edit the original
     line. Add the revision underneath it, like this:

         ## 1. Retrieved chunks contain the answer

         For at least 4 of my 5 test questions, the retrieved chunks include
         one that contains the answer.

         **Why this target:** ...

         > **Revised in unit 2:** For at least 4 of 5 questions, the top three
         > results contain the answer.
         >
         > **Why revised:** I couldn't judge "the chunks include one that
         > contains the answer" the same way twice — I scored two questions
         > differently on Monday than on Wednesday. The new version is
         > something I can actually check.

     That's a revision because the criterion couldn't be MEASURED.

     Lowering a target because you missed it is not a revision, and it costs
     you the point:

         ✗ "I said 4 of 5 but got 2 of 5, so 2 of 5 is more realistic."

     A number you missed stays where it is, gets diagnosed, and gets a fix
     attempted. That's where the points are.

     The whole reason the originals stay visible is so someone can see what you
     said before you knew the answer.
     ───────────────────────────────────────────────────────────────────────── -->
