# context_manager

Context managing module for vision/language models (VLM planning loops).

Target assumptions (current):
- Model: qwen3-vl-32b
- Loop: ~1 FPS
- Observations can be image/video/text upstream, but will be **encoded into text** before entering this module.

## What this repo is building

Core responsibilities:
1) Context summarization / compression (trigger-based)
2) Context record / memory (later: POST to external local-memory DB)
3) Context history (bounded timeline)
4) Context isolate (optional namespaces)

We use **LangGraph** as the orchestration layer.

## Quickstart (dev)

Because macOS Python may be externally managed, use a venv:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
python examples/langgraph_m1.py
```

## Reporting

- Worklog: `ops/WORKLOG.md`
- Reports live in `reports/`
  - Daily: `reports/daily/YYYY-MM-DD.md`
  - Weekly: `reports/weekly/YYYY-WW.md`
  - Monthly: `reports/monthly/YYYY-MM.md`
  - Year-end: `reports/yearly/YYYY-12-retro.md`

Templates are in `reports/templates/`.
