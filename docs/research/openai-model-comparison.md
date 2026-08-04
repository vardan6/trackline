# OpenAI GPT-5 Model Comparison

Prices below are standard API text-token rates as of July 19, 2026. The price
format is **input / cached input / output**. Relative cost compares input and
output rates with GPT-5.6 Sol as `1.0x`.

| Model | Practical role / positioning | API price / 1M tokens | Relative cost vs Sol (input / output) | Best use |
|---|---|---:|---:|---|
| [GPT-5.6 Sol](https://developers.openai.com/api/docs/models/gpt-5.6-sol) | Current frontier GPT-5.6 tier; highest reasoning and professional-work capability | **$5.00 / $0.50 / $30.00** | **1.00x / 1.00x** | Hard coding-agent work, architecture, difficult debugging, ambiguous refactors, deep research, and long-horizon planning |
| [GPT-5.6 Terra](https://developers.openai.com/api/docs/models/gpt-5.6-terra) | Balanced GPT-5.6 tier; roughly replaces the older "mini" role | **$2.50 / $0.25 / $15.00** | **0.50x / 0.50x** | Default coding workhorse, code review, normal research, planning, tool use, and moderately complex autonomous tasks |
| [GPT-5.6 Luna](https://developers.openai.com/api/docs/models/gpt-5.6-luna) | Cost-sensitive GPT-5.6 tier; roughly replaces the older "nano" role, but is substantially more expensive than GPT-5.4 nano | **$1.00 / $0.10 / $6.00** | **0.20x / 0.20x** | High-volume subagents, repository search, extraction, summarization, test generation, and clear, narrowly scoped edits |
| [GPT-5.6](https://developers.openai.com/api/docs/models/gpt-5.6-sol) | **Alias for GPT-5.6 Sol**, not a separate model tier | **$5.00 / $0.50 / $30.00** | **1.00x / 1.00x** | Same work as Sol; convenient alias when a separately named Sol deployment is unnecessary |
| [GPT-5.5](https://developers.openai.com/api/docs/models/gpt-5.5) | Previous-generation frontier model for coding and professional work | **$5.00 / $0.50 / $30.00** | **1.00x / 1.00x** | Existing pinned workflows, regression-sensitive applications, or evaluations requiring GPT-5.5 behavior; otherwise Sol is the natural successor |
| [GPT-5.4](https://developers.openai.com/api/docs/models/gpt-5.4) | Earlier frontier model, now a relatively affordable high-capability option | **$2.50 / $0.25 / $15.00** | **0.50x / 0.50x** | Complex coding and professional work where established GPT-5.4 behavior is sufficient and Sol-level capability is unnecessary |
| [GPT-5.4 mini](https://developers.openai.com/api/docs/models/gpt-5.4-mini) | Strong compact model specifically positioned for coding, computer use, and subagents | **$0.75 / $0.075 / $4.50** | **0.15x / 0.15x** | Economical coding agents, parallel subagents, computer-use workflows, routine implementation, tests, and structured transformations |
| [GPT-5.4 nano](https://developers.openai.com/api/docs/models/gpt-5.4-nano) | Cheapest GPT-5.4-class model for simple, high-volume processing | **$0.20 / $0.02 / $1.25** | **0.04x / 0.042x** | Classification, ranking, extraction, routing, validation, metadata generation, and very simple subagent tasks |
| [GPT-5.3-Codex](https://developers.openai.com/api/docs/models/gpt-5.3-codex) | Older specialist optimized explicitly for agentic coding in Codex-like environments | **$1.75 / $0.175 / $14.00** | **0.35x / 0.47x** | Existing Codex-oriented coding pipelines, autonomous edit-test-debug loops, and coding-specific workloads; less compelling for broad research or general professional tasks |

## Practical Conclusions

- **Best maximum-quality choice:** GPT-5.6 Sol.
- **Best general cost/quality choice:** GPT-5.6 Terra.
- **Best economical modern GPT-5.6 agent:** GPT-5.6 Luna.
- **Cheapest useful coding/subagent model:** GPT-5.4 mini.
- **Cheapest routing/extraction worker:** GPT-5.4 nano.
- **GPT-5.3-Codex remains coding-specialized**, but GPT-5.6 Luna is cheaper on
  output and has a much larger context window. Terra or Sol are preferable when
  judgment and planning matter.
- **GPT-5.5 has the same token price as Sol**, so its main reason for continued
  use is behavioral stability or pinned evaluations, not cost.

These ratios describe billed tokens, not total task cost. A cheaper model can
consume more tokens, require retries, or produce changes that need correction.

GPT-5.6 Sol, Terra, and Luna, GPT-5.5, and GPT-5.4 apply higher rates to very
long requests. Above 272K input tokens, the documented multiplier is generally
`2x` input and `1.5x` output for the full request or session.
