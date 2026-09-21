# Original + softer statement search

September 20, 2026. Frozen scoped-v2 expectations, normal retrieval only.
104 live Jev requests, one repeat, batch size four; 15.72 seconds total.

| Metric | Revised baseline | Softer search | Change |
|---|---:|---:|---:|
| F1 | 72.2% | 77.8% | +5.6 percentage points |
| Precision | 92.9% (13/14) | 100.0% (14/14) | +7.1 points |
| Recall | 59.1% (13/22) | 63.6% (14/22) | +4.5 points |
| Unauthorized releases | 1 | 0 | -1 |
| Needed facts withheld | 8 | 6 | -2 |
| Search misses | 1 | 2 | +1 |

No excessive-detail failures or API errors. Eight required facts still failed.
Search coverage worsened despite improved overall scores. One model run does not
establish that the retrieval change caused a reliable improvement.

Implementation: original vectors retain sqlite-vec retrieval; softer text is
embedded independently and scanned locally, with embeddings cached in memory.
Take up to 16 candidates from each representation, merge by fact ID with minimum
cosine distance, apply the unchanged keyword bonus, and keep eight. No role,
permission, threshold, fixture, or expected-outcome changes. No database migration
is required; newly approved facts participate on the next search.

Run artifacts: `/var/folders/h9/0tp63nds6p59byrdbk0zksyw0000gn/T/need2know-eval-pxar6ljs/`.
The temporary directory contains report.txt, results.json, matrix.csv, audit.db.
Exit code 1 indicates remaining benchmark mismatches, not a crash.

Reproduce from the project directory:

```sh
uv run python scripts/evaluate_memory.py --benchmark scoped-v2 --mode retrieval
```
