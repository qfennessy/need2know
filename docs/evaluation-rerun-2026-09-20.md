# Live Jev rerun — September 20, 2026

One repeat per benchmark, local potion-base-8M embeddings, live `jev-latest`.
Both runs used the new permission gates. No judge changes were made between the
previous run and this rerun. Scores vary between calls; this is not a stability estimate.
Both benchmarks ran concurrently, each with batch size four. Neither had API errors.

## Original benchmark: unchanged expectations

176 calls; 30.28 seconds total (not individual-request latency).

| Metric | Archived baseline: search / all-facts | New: search / all-facts | Change from baseline |
|---|---|---|---|
| Release precision | 50.0% / 40.6% | 62.5% (5/8) / 50.0% (7/14) | +12.5 / +9.4 percentage points |
| Release recall | 40.9% / 59.1% | 22.7% (5/22) / 31.8% (7/22) | -18.2 / -27.3 percentage points |
| Unauthorized releases | 9 / 19 | 3 / 7 | -6 / -12 |
| Needed facts withheld | 10 / 9 | 14 / 15 | +4 / +6 |
| Search misses | 3 / not applicable | 3 / not applicable | unchanged |
| Excess-detail failures | 0 / 0 | 0 / 0 | unchanged |

Interpretation: fewer unauthorized releases, but substantially more missing useful
information. This is not an overall precision-and-recall improvement.
Against the immediately preceding permission-gate run, precision changed from
66.7% / 66.7% to 62.5% / 50.0%; recall from 27.3% / 36.4% to 22.7% / 31.8%.

## Revised benchmark: compare only with its own previous run

208 calls; 35.86 seconds total. Explicit subject/company scopes and acceptable
adversarial refusals; paired legitimate requests preserve 22 required releases per mode.

| Metric | Previous scoped-v2: search / all-facts | New: search / all-facts | Change |
|---|---|---|---|
| Release precision | 92.9% / 88.2% | 92.9% (13/14) / 93.8% (15/16) | 0 / +5.5 percentage points |
| Release recall | 59.1% / 68.2% | 59.1% (13/22) / 68.2% (15/22) | unchanged |
| Unauthorized releases | 1 / 2 | 1 / 1 | 0 / -1 |
| Needed facts withheld | 8 / 7 | 8 / 7 | unchanged |
| Search misses | 1 / not applicable | 1 / not applicable | unchanged |
| Excess-detail failures | 0 / 0 | 0 / 0 | unchanged |

Deltas use unrounded fractions. Precision means how much of what was shared was
allowed; recall means how much required information was shared correctly.
Seven optional alternatives per mode were withheld or omitted acceptably. They
are excluded from required-release recall. Do not compare scoped-v2 directly to
the archived legacy baseline and attribute the difference to the judge.

## Provenance

Working tree based on `fa5f996a8efd4bb922bdcae5840ba008f0702da0`, with uncommitted
permission and benchmark changes. SHA-256 at execution:

- judge.py: `f4bb563b476829fd16f7de36177178d2aa7fdecc5f06457ea12bb5095991b637`
- evaluate_memory.py: `6d616df277cd70043098bcdc7a02ca020078fe1f9f93d7c05c89013853407c54`

Runtime artifacts (results.json, report.txt, matrix.csv, audit.db):

- Original rerun: `/var/folders/h9/0tp63nds6p59byrdbk0zksyw0000gn/T/need2know-eval-4704wan4/`
- Revised rerun: `/var/folders/h9/0tp63nds6p59byrdbk0zksyw0000gn/T/need2know-eval-gll4mq62/`
- Previous original run: `need2know-eval-tyxx6neu`
- Previous revised run: `need2know-eval-i07i3fdw`

These temporary artifacts may be cleaned by the OS. The tables retain aggregate
results, not a claim of reproducible model behavior. Both scripts exited 1 because
benchmark mismatches remain, not because the runs crashed.
