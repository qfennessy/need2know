# Recorded evaluation baseline

Recorded September 20, 2026 from the existing live run `need2know-eval-u46_uo94`.
This is an archived measurement, not a new run or a guarantee of current behavior.

176 requests: 11 questions × 8 roles × 2 modes, one repeat, 15 scored facts per
request. Judge: `jev-latest`. Embeddings: local `minishlab/potion-base-8M`.
Four concurrent requests; total elapsed time 27.21 seconds.

| Metric | Normal retrieval | All facts given to Jev | Plain-language explanation |
|---|---:|---:|---|
| Release precision | 50.0% (9/18) | 40.6% (13/32) | Of everything shared, how much was allowed? Higher is better. |
| Release recall | 40.9% (9/22) | 59.1% (13/22) | Of everything needed, how much was shared correctly? Higher is better. |
| Unauthorized releases | 9 | 19 | Facts shared when the benchmark expected privacy. Lower is better. |
| Needed facts withheld | 10 | 9 | Jev saw a needed fact but did not share it. Lower is better. |
| Needed facts missed by search | 3 | Not applicable | Needed facts never reached Jev. Lower is better. |
| Excess-detail failures | 0 | 0 | Full text shared when only softer text was allowed. Lower is better. |
| Failed API calls | 0 | 0 | Requests that could not be judged successfully. |
| Completely correct requests | 77/88 (87.5%) | 78/88 (88.6%) | Every fact decision in the request matched expectations. |

Normal retrieval found 19 of the 22 needed facts: retrieval recall **86.4%**.
Correctly judged private facts: 676 / 1,279 respectively. Normal retrieval also
omitted 613 facts correctly; omissions are not judged denials.

Precision = correct releases / all releases. Recall = correct releases / all
expected releases, including search misses. A release with excessive detail is
not correct. No easy negative cells are included in these two denominators.
Completely correct requests were calculated from archived rows grouped by query ID.

## Comparison rules and limitations

- Keep the questions, roles, facts and expected outcomes unchanged when comparing
  improvements. Do not ease the benchmark to improve the numbers.
- Report both modes separately. All-facts bypasses search; it is not production
  end-to-end performance. Aggregate accuracy can hide poor useful-fact recall.
- This run uses handwritten softer statements, not Sonnet generation, and does
  not test live MCP clients. One repeat does not establish model stability.
- A later user-supplied run showed a medication disclosure to counsel. The zero
  excess-detail count here is specific to this run, not a safety guarantee.
- Individual-request end-to-end median and p95 latency were not measured. The
  27.21-second parallel-run duration is not individual-request latency.
- The original run did not capture a source commit or immutable model revision;
  `jev-latest` is a mutable model name. Do not claim exact reproducibility.

Source artifacts: `results.json`, `matrix.csv`, `report.md`, and `audit.db` in
`/var/folders/h9/0tp63nds6p59byrdbk0zksyw0000gn/T/need2know-eval-u46_uo94/`.
This temporary location may be cleaned by the operating system; the aggregate
baseline above is retained in this document.
