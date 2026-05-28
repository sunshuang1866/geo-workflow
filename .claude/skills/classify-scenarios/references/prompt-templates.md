# Prompt Templates — classify-scenarios

## TAXONOMY_EXTRACTION

Used by `extract-taxonomy.py` to derive an application scenario taxonomy from a community documentation directory listing.

```
You are a technical documentation analyst. Below is a list of pages from an open-source community's official documentation site.

Your task: Identify 5–8 distinct application scenario categories that best describe how users actually use this software community (not just doc sections).

Rules:
- Each category must be a concrete, user-facing scenario (e.g. "安装与部署", "内核驱动开发", "容器虚拟化").
- Avoid overly generic categories like "其他" or "通用" unless there truly is no better fit.
- Avoid duplicates — merge semantically overlapping categories.
- Return exactly a JSON array of objects, one per scenario. No prose, no markdown code fences.

Output format:
[
  {"key": "install_deploy", "label": "安装与部署"},
  {"key": "kernel_driver", "label": "内核与驱动"},
  ...
]

Documentation pages:
{DOC_PAGES}
```

---

## QUESTION_CLASSIFICATION

Used by `classify-questions.py` to assign a scenario label to each question in a batch.

```
You are a technical content classifier. You will classify user questions about a software community into application scenario categories.

Scenario taxonomy (use ONLY these keys and labels):
{TAXONOMY_JSON}

Rules:
- Assign exactly ONE scenario key to each question.
- Choose the scenario that best matches the QUESTION INTENT (what the user is trying to do), not just keyword overlap.
- If no scenario fits well, use "general" (label: "通用").
- Return ONLY a JSON object mapping question_id to scenario_key. No prose, no markdown.

Output format:
{"q_001": "install_deploy", "q_002": "kernel_driver", ...}

Questions to classify:
{QUESTIONS_JSON}
```
