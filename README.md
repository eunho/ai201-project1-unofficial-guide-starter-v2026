# The Unofficial Guide

**Author:** Student  
**Corpus:** `campus_life`

> **This file is your submission.** Fill it in as you go — most sections get
> written during the milestone that produces them, not at the end.
>
> How the starter works, and every command you'll need, is in `RUNNING.md`.
> Leave that file alone.
>
> **Paste everything as text.** No screenshots, no video. A typed table gets
> full credit; a picture of the same table gets none.

---

# Unit 1

## What This Does

This system is an end-to-end grounded question-answering assistant (RAG pipeline) built over the `campus_life` corpus—a collection of 88 student-authored guides, administrative tips, and campus reviews. It answers practical questions about university life, including dining hall wait times and hours, dorm facilities (laundry, noise, and room layouts), course grading schemes, and registrar deadlines. Every query is evaluated by a cosine-distance relevance gate before reaching the model: queries that lack supporting documents are stopped immediately with a refusal, while valid questions receive concise answers grounded strictly in retrieved chunks, each citing its source document.

## Chunking Strategy

**Chunk size:** 400 characters  
**Overlap:** 80 characters  

The `campus_life` corpus consists of 88 short student-written documents averaging approximately 317 characters (ranging from 178 to 554 characters). The starter's baseline fixed-window chunker used 800 characters with 120 character overlap, which left all 88 documents un-split as single chunks. However, arbitrarily chopping at character boundaries on multi-topic posts causes severed sentences and strips crucial context (such as the document title naming the dining hall or residence hall).

I set the chunk size to 400 characters with 80 characters of overlap and replaced the chunking logic with a paragraph- and sentence-boundary aware strategy (`chunker.py::split_documents`). Single-topic posts under 400 characters remain intact as cohesive standalone chunks (~70% of the corpus). For longer documents that cover multiple distinct facets (e.g., room layout, laundry fees, and noise ratings), the chunker splits along paragraph breaks and sentences, prepending the document title to each subsequent chunk. This ensures that every chunk remains an independently answerable, complete thought.

## Sample Chunks

**Chunk 1** — source: `admin_add_drop_deadline.txt#0` — produced by: `chunker.py::split_documents`

```
On the add/drop deadline

You can add a course through the end of the second week. Dropping is a longer window — through the end of week six — but a drop after week two shows as a W on your transcript. Nothing anywhere on the registrar's site says this plainly, and students find out from each other.
```

**Chunk 2** — source: `course_biol_160_exams.txt#0` — produced by: `chunker.py::split_documents`

```
BIOL 160 Cell Biology — assessment

Four unit tests and a cumulative final. Not curved.

The unit tests come fast, roughly every three weeks; falling behind once is very hard to recover from.
```

**Chunk 3** — source: `course_math_220.txt#0` — produced by: `chunker.py::split_documents`

```
MATH 220 Linear Algebra

I lived here my sophomore year. Format is chalk-and-talk lecture, weekly problem sets marked for correctness. Assessment: two midterms and a cumulative final. Curved to a b- median.

Expect 6 to 8 hours a week, almost all of it on problem sets.

The one piece of advice: the problem sets are the course; the lectures make sense afterwards rather than during.
```

**Chunk 4** — source: `dining_the_atrium.txt#1` — produced by: `chunker.py::split_documents`

```
The Atrium

Hours are 8:00am to 6:00pm weekdays. Costs one meal swipe for a sandwich-plus-drink combination, or à la carte.
```

**Chunk 5** — source: `housing_innisfree_hall_laundry.txt#0` — produced by: `chunker.py::split_documents`

```
Laundry in Innisfree Hall

Machines take $1.75 wash, $1.75 dry, app-based. There are eight washers and six dryers for the building, which is the wrong ratio and means the dryers back up on Sunday evenings.

Best time to do laundry here is Tuesday or Wednesday morning. Sunday after 6pm you will wait.
```

## Sample Answer

**Question:** How does the housing lottery decide selection order for juniors and seniors?

**Answer:**

```
Juniors and seniors are ordered by accumulated credit hours first, with a random tie-break used if needed (*admin_housing_lottery.txt*).

Sources retrieved: admin_housing_lottery.txt, admin_parking_permits.txt, advising_registration.txt, dining_the_atrium_followup.txt, housing_tamsin_court.txt
```

**My relevance cutoff:** `0.60`

To determine the relevance cutoff, I measured the best cosine distance for my five in-scope test questions and the five out-of-scope questions from `OUT_OF_SCOPE`. 

The in-scope distances formed a tight cluster between 0.198 and 0.400 (mean ~0.287). The out-of-scope questions clustered far higher, between 0.825 and 0.934 (mean ~0.877). This creates an unambiguous gap of 0.425 between 0.400 and 0.825.

I selected a cutoff threshold of `0.60`. This provides a generous safety margin (~0.20 above the highest in-scope question) so slight variations in user phrasing will not trigger false refusals, while sitting ~0.225 below the closest out-of-scope question to ensure non-corpus queries are consistently blocked before reaching the generation model.

| Question | In corpus? | Best distance |
|---|---|---|
| How does the housing lottery decide selection order for juniors and seniors? | Yes | 0.207 |
| What are the library hours during reading week compared to normal term? | Yes | 0.400 |
| What happens if a student drops a course after the second week? | Yes | 0.358 |
| How long are the wait times at Kestrel Commons during peak lunch between 12:15 and 1:00? | Yes | 0.198 |
| How can students get the campus bookstore to price match textbook prices? | Yes | 0.272 |
| What is the capital of Mongolia? | No | 0.825 |
| How do I change the oil in a diesel engine? | No | 0.934 |
| Who won the 1994 World Cup? | No | 0.886 |
| What is the recommended dosage of ibuprofen for a headache? | No | 0.844 |
| How do I write a for loop in Rust? | No | 0.896 |

## How I Used AI

**1. Chunking Strategy & Header Propagation:**  
I asked the AI assistant to help design a chunking function that splits documents on natural paragraph boundaries (`\n\n`) rather than fixed character windows. The initial snippet split paragraphs cleanly but treated each paragraph in isolation. For longer dorm and dining reviews, this stripped the title line (e.g. `Innisfree Hall` or `Kestrel Commons`) from later paragraphs describing laundry costs or hours, causing downstream vector searches to lose the entity context. I modified the logic to extract the document header/title and prepend it to every subsequent chunk if not already present, ensuring every chunk stands on its own.

**2. Relevance Gate Threshold Selection:**  
I used the AI assistant to query the vector store for both my 5 in-scope test questions and the 5 out-of-scope control questions from `OUT_OF_SCOPE` and tabulate their nearest cosine distances. The assistant noted the gap between the highest in-scope distance (0.400) and lowest out-of-scope distance (0.825) and initially proposed a tighter cutoff of 0.50. I adjusted the cutoff to 0.60 to build in a generous buffer (~0.20 above 0.400) so that real user queries with alternate vocabulary wouldn't be falsely rejected by the gate.

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

- Produced by: `run_eval.py::main`
- Run log evidence file: `results/run_2026-09-23_1625_before.md`
- Retrieval: `store.py::search`, chunks from `chunker.py::split_documents`
- Corpus: `campus_life` (index variant `default`)
- top-k: 5 · relevance cutoff: 0.60
- Runs per question: 3, caching off

| Criterion | Target | Run 1 | Run 2 | Run 3 | Verdict |
|---|---|---|---|---|---|
| 1. Retrieved chunk contains the answer | 4 of 5 | 5/5 | 5/5 | 5/5 | MET |
| 2. Every answer names a source | 5 of 5 | 5/5 | 5/5 | 5/5 | MET |
| 3. Gate stops out-of-corpus questions | 4 of 5 | 5/5 | 5/5 | 5/5 | MET |
| 4. Standalone chunk integrity | 4 of 5 | 5/5 | 5/5 | 5/5 | MET |
| 5. Ground-truth source attribution accuracy | 5 of 5 | 5/5 | 5/5 | 5/5 | MET |

### Real output from Run 1

#### Criterion 1, 2, & 5: Generated Answers and Source Attribution
Produced by `generate.py::answer_from_chunks` via `run_eval.py::run_once`:

- **Question 1:** "How does the housing lottery decide selection order for juniors and seniors?"  
  *Best distance:* 0.2073 (passed gate)  
  *Sources retrieved:* `admin_housing_lottery.txt`, `admin_parking_permits.txt`, `advising_registration.txt`, `dining_the_atrium_followup.txt`, `housing_tamsin_court.txt`  
  ```
  Juniors and seniors are ordered by accumulated credit hours first, with random tie-breaking used only when there is a tie. 

  Source: admin_housing_lottery.txt
  ```

- **Question 2:** "What are the library hours during reading week compared to normal term?"  
  *Best distance:* 0.4002 (passed gate)  
  *Sources retrieved:* `course_hist_118_workload.txt`, `housing_morrow_house_noise.txt`, `money_jobs.txt`, `money_textbooks.txt`, `study_library_hours.txt`  
  ```
  During reading week, the library is open until 10pm, whereas it is open until 2am during term. 

  Source: study_library_hours.txt
  ```

- **Question 3:** "What happens if a student drops a course after the second week?"  
  *Best distance:* 0.3576 (passed gate)  
  *Sources retrieved:* `admin_add_drop_deadline.txt`, `admin_grade_appeals.txt`, `admin_pass_fail_option.txt`, `admin_wifi_and_accounts.txt`, `admin_withdrawal_deadline.txt`  
  ```
  If a student drops a course after the second week, it shows as a "W" on their transcript (admin_add_drop_deadline.txt).
  ```

- **Question 4:** "How long are the wait times at Kestrel Commons during peak lunch between 12:15 and 1:00?"  
  *Best distance:* 0.1982 (passed gate)  
  *Sources retrieved:* `dining_halden_hall_followup.txt`, `dining_kestrel_commons.txt`, `dining_kestrel_commons_followup.txt`, `dining_pellew_dining_hall_followup.txt`, `dining_the_ridgeway_cafe_followup.txt`  
  ```
  The wait times at Kestrel Commons are 20 to 25 minutes between 12:15 and 1:00. This information comes from the documents `dining_kestrel_commons.txt` and `dining_kestrel_commons_followup.txt`.
  ```

- **Question 5:** "How can students get the campus bookstore to price match textbook prices?"  
  *Best distance:* 0.2719 (passed gate)  
  *Sources retrieved:* `admin_library_holds.txt`, `admin_printing_quota.txt`, `course_econ_101.txt`, `money_textbooks.txt`, `study_group_rooms.txt`  
  ```
  To get the campus store to price-match, students must ask at the counter and show the other listing on their phone (money_textbooks.txt).
  ```

#### Criterion 3: Relevance Gate on Out-of-Scope Questions
Produced by `run_eval.py::check_out_of_scope` (calling `gate.py::check` with cutoff `0.60`):

| Out-of-scope question | Best distance | Gate decision |
|---|---|---|
| What is the capital of Mongolia? | 0.825 | refused |
| How do I change the oil in a diesel engine? | 0.934 | refused |
| Who won the 1994 World Cup? | 0.886 | refused |
| What is the recommended dosage of ibuprofen for a headache? | 0.844 | refused |
| How do I write a for loop in Rust? | 0.896 | refused |

*Gate outcome:* Refused 5 of 5 out-of-scope questions.

#### Criterion 4: Standalone Chunk Integrity
Sample top-1 retrieved chunk produced by `store.py::search` (chunked by `chunker.py::split_documents`), verifying complete thought and boundary preservation:

*Source:* `admin_housing_lottery.txt#0`
```
On the housing lottery

The housing lottery is not random in the way most people assume. Rising sophomores get a number drawn at random, but juniors and seniors are ordered by accumulated credit hours first, and only tie-break randomly. That means a senior who took summer courses reliably beats a senior who didn't. Numbers come out the second week of March and selection runs over four evenings.
```

## Verdicts

| # | Criterion | Target | Verdict | How I decided |
|---|---|---|---|---|
| 1 | Retrieved chunk contains the answer | 4 of 5 | MET | Across all three evaluation runs, the retrieved chunks for 5 of 5 questions contained the exact ground-truth passage (clearing the 4 of 5 target on every trial). |
| 2 | Every answer names a source | 5 of 5 | MET | All three runs scored 5 of 5 because every generated response strictly adhered to the system prompt and named its source document filename. |
| 3 | Gate stops out-of-corpus questions | 4 of 5 | MET | The relevance gate rejected all 5 out-of-scope questions with cosine distances between 0.825 and 0.934 (well above the 0.60 threshold). |
| 4 | Standalone chunk integrity | 4 of 5 | MET | For all 5 test questions across all three runs, 5 of 5 top-1 retrieved chunks formed self-contained, grammatically complete units with intact sentence boundaries and preserved title headers. |
| 5 | Ground-truth source attribution accuracy | 5 of 5 | MET | In all three runs, 5 of 5 answers cited the exact document containing the factual answer without attributing false claims to distractor chunks. |

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
