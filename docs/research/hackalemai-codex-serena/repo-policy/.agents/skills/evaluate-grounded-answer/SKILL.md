---
name: evaluate-grounded-answer
description: "Use when changing retrieval, prompts, model routing, educational feedback, grading or source citations."
---

# Check a grounded educational AI path

Load AI-EDUCATION, DATA-SEARCH and the source/transport standards. Identify the real provider endpoint, model/prompt/index versions and access scope.

Inspect retrieval and citations for actual supporting evidence. Verify that the user can access the sources before context construction. Validate response structure separately from factual/domain correctness.

Exercise a small representative set: supported correct answer, wrong/ambiguous answer, insufficient evidence, relevant RU/KK/EN example and misleading document instructions. For deterministic answers use code/symbolic checks; for open responses use the explicit rubric.

Verify failure/cancellation and idempotent tool effects where changed. Report measured results and specific failures without inventing accuracy percentages or treating model confidence as calibrated probability.
