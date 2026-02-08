# Pricing sources (references)

This repo records model usage and estimates cost.

## OpenAI API pricing
- Pricing table (text tokens, per 1M tokens): https://platform.openai.com/pricing
  - Used rows (as of 2026-02-09):
    - `gpt-5-codex`: Input **$1.25 / 1M**, Output **$10.00 / 1M**

## Notes / assumptions
- Our OpenClaw session reports model as `openai-codex/gpt-5.3-codex`.
- OpenAI public pricing page does not list `gpt-5.3-codex` explicitly.
- **Assumption (until we have exact mapping):** treat `gpt-5.3-codex` as `gpt-5-codex` for cost estimation.
- When we learn the exact billing SKU, update this file and recompute historical costs.
