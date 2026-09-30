# Day 4 — Where Memory Lives and Why Retrieval Is Harder Than Storage

Experiments behind the Day 4 post. They take the Day 3 code and push it until it
breaks, in two different ways: speed (a systems problem) and relevance (the hard one).

Nothing here changes Day 3. `bench_scale.py` imports `../day3/memory.py` as-is, and
the other scripts copy Day 3's cosine similarity and ranking formula verbatim:

```text
score = similarity * 0.7 + importance * 0.2 + confidence * 0.1
```

## Prerequisites

* Python 3.11+ with `numpy` (the scripts talk to Ollama over plain HTTP, no `ollama` package needed)
* [Ollama](https://ollama.com/) running locally with `nomic-embed-text`

```bash
ollama pull nomic-embed-text
pip install numpy        # or: uv run --with numpy python <script>.py
```

## The experiments

| Script | What it measures | Needs Ollama? | Runtime |
| ------ | ---------------- | ------------- | ------- |
| `bench_scale.py` | Time to store one memory vs retrieve the top 3 as the table grows from 10 to 100,000 memories (random 768-d vectors) | No | ~1 min + ~30 s per 100k retrieval; writes a ~1.6 GB `scale.db` |
| `bench_breakdown.py` | Where retrieval time goes (SQL fetch vs `json.loads` vs cosine), and the same brute-force search in NumPy up to 1M memories | No | ~1 min; run `bench_scale.py` first; needs ~4 GB RAM |
| `relevance.py` | An 11-memory store with real embeddings: ranking, the narrow similarity band, thresholds, Kubernetes-then/ECS-now, with and without nomic task prefixes | Yes | seconds |
| `growth.py` | Does the right memory stay in the top 3 as 0 to 1,000 other memories are added? 12 memory/question pairs + template-generated distractors | Yes | ~30 s on CPU |
| `emb.py` | Tiny helper: batch embeddings via Ollama `/api/embed`, plus the Day 3 score | - | - |

Run from this folder:

```bash
cd day4
python bench_scale.py
python bench_breakdown.py
python relevance.py
python growth.py
```

`scale.db` is a throwaway benchmark file; delete it afterwards.

## Results

The `*-output.txt` files are the outputs quoted in the post, recorded on
30 September 2026 on an 8-vCPU Linux machine with Python 3.11. Absolute timings
will differ on your machine; the shape of the curves should not.

Headline numbers:

* Store one memory: ~4 ms at 10 rows and at 100,000 rows. Retrieve top 3: 5 ms at 10, **30.8 s** at 100,000.
* At 10,000 memories, `json.loads()` of the TEXT embeddings is ~2.2 s of the ~3 s retrieval.
* Right memory in the top 3: **9/12** with no extra memories, **3/12** with 1,000.
* "User is allergic to peanuts" for "Suggest a snack": rank 3 with 12 memories, rank **29** with 1,000 more.

## Caveats

* The distractor memories in `growth.py` come from a template, so they repeat
  phrases more than real memories would. Twelve questions is a demonstration,
  not a benchmark.
* Importance and confidence values are randomised within plausible ranges.
* `growth.py` uses a fixed random seed, but embedding values can vary slightly
  across Ollama versions and hardware.
