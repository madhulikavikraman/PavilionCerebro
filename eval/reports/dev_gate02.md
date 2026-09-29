# Eval report: dev_gate02

Images scored: 50 of 50 in manifest. All CIs are 95 percent bootstrap (1000 resamples). Public datasets, not customer imagery; do not extrapolate to field performance.

## Gate (stage A): damage_present, positive = routed to grader

| Metric | Value | 95% CI | n |
|---|---|---|---|
| Recall (headline) | 78.9% | 65.9% to 90.5% | 50 |
| Precision | 81.1% | 66.7% to 92.1% | 50 |
| F1 | 80.0% | 68.6% to 88.6% | 50 |
| Routing fraction | 74.0% | | 50 |
| Marked unusable | 0 | | |

Per dataset:

| Dataset | n | Recall | Precision | Routed |
|---|---|---|---|---|
| corrosion_cs | 15 | 100.0% | 100.0% | 15 |
| dacl10k | 15 | 100.0% | 71.4% | 14 |
| ir_solar | 12 | 0.0% | 0.0% | 0 |
| rescuenet | 8 | 100.0% | 62.5% | 8 |

Missed damaged images (8): ir_test_00364, ir_test_02154, ir_test_02175, ir_test_00163, ir_test_02185, ir_test_01450, ir_test_01695, ir_test_00848

## Grading (stage C), per asset class, worst finding per image vs dataset truth

### steel_coating

n routed with truth: 15; U rate 100.0%; nothing assessed.

### building_disaster

n routed with truth: 8; U rate 100.0%; nothing assessed.

## Ops (measured from call log)

| Stage | Calls | Median seconds | USD total | Models |
|---|---|---|---|---|
| gate | 50 | 4.98 | 0.0 | qwen3-vl:4b-instruct |

USD per image (all stages): 0.0
