# dacl10k team-grading rubric (severity 1 to 4)

Written 2026-09-24 before any model output (docs/decisions.md D-007). Two teammates grade each dacl10k eval image independently using only this rubric and the image; Cohen's kappa is reported; disagreements are adjudicated by a third teammate and the adjudicated grade is used. Rows are marked `grade_source: team-graded` in the manifest.

| Grade | Name | Assign when |
|---|---|---|
| 1 | Minor (MBEI CS2-like) | Only hairline cracks, light efflorescence, wet spots, surface weathering, or rust staining without spalling. Nothing exposed. |
| 2 | Moderate (MBEI CS3-like) | Spalling or cavities without exposed reinforcement, wide or map cracking, heavy efflorescence with rust staining, hollow areas. |
| 3 | Major | Exposed reinforcement (ExposedRebars) or spalling with section loss visible, or washouts / concrete corrosion over a large area. |
| 4 | Critical | Exposed reinforcement with visible bar section loss, displaced or missing concrete on a bearing area, or any sign of instability. |

Rules: grade the worst visible defect, not the average; ignore graffiti, remaining formwork and equipment; if the image is too blurred or dark to judge, write U. Record grades in `eval/team_grades/<initials>.csv` with columns `image_id,grade,note`.
