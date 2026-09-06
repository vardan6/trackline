# OpenAI GPT-5 and GPT-6 Model Comparison

Prices below are standard API text-token rates as of September 6, 2026. The price
format is **input / cached input / output**. Relative cost compares input and
output rates with GPT-5.6 Sol as `1.0x`, rounded to three decimals where needed.
Rates exclude tool fees and processing-mode or regional adjustments. Sol’s
current pricing is promotional through at least November 21, 2026.
See [official API pricing](https://developers.openai.com/api/docs/pricing).
Practical roles and recommendations below are judgments to validate on your workload,
not measured benchmark rankings.

| Model | Practical role / positioning | API price / 1M tokens | Relative cost vs Sol (input / output) | Best use |
|---|---|---:|---:|---|
| [GPT-6 Astra](https://developers.openai.com/api/docs/models/gpt-6-astra) | Highest-capability model for complex end-to-end work | **$10.00 / $1.00 / $50.00** | **2.50x / 2.50x** | Hardest coding, research, computer-use, and document workflows |
| [GPT-5.6](https://developers.openai.com/api/docs/models/gpt-5.6-sol) | **Alias for GPT-5.6 Sol**, not a separate model tier | **$4.00 / $0.40 / $20.00** | **1.00x / 1.00x** | Same work as Sol; convenient alias when a separately named Sol deployment is unnecessary |
| [GPT-5.6 Sol](https://developers.openai.com/api/docs/models/gpt-5.6-sol) | Highest GPT-5.6 tier; lower token cost than Astra | **$4.00 / $0.40 / $20.00** | **1.00x / 1.00x** | Hard coding-agent work, architecture, difficult debugging, ambiguous refactors, deep research, and long-horizon planning |
| [GPT-5.6 Terra](https://developers.openai.com/api/docs/models/gpt-5.6-terra) | Balanced GPT-5.6 tier; roughly replaces the older "mini" role | **$2.00 / $0.20 / $12.00** | **0.50x / 0.60x** | Default coding workhorse, code review, normal research, planning, tool use, and moderately complex autonomous tasks |
| [GPT-5.6 Luna](https://developers.openai.com/api/docs/models/gpt-5.6-luna) | Cost-sensitive GPT-5.6 tier; roughly replaces the older "nano" role | **$0.20 / $0.02 / $1.20** | **0.05x / 0.06x** | High-volume subagents, repository search, extraction, summarization, test generation, and clear, narrowly scoped edits |
| [GPT-5.5](https://developers.openai.com/api/docs/models/gpt-5.5) | Previous-generation frontier model for coding and professional work | **$5.00 / $0.50 / $30.00** | **1.25x / 1.50x** | Existing pinned workflows, regression-sensitive applications, or evaluations requiring GPT-5.5 behavior; otherwise Sol is the natural successor |
| [GPT-5.4](https://developers.openai.com/api/docs/models/gpt-5.4) | Earlier frontier model, now a relatively affordable high-capability option | **$2.50 / $0.25 / $15.00** | **0.625x / 0.75x** | Complex coding and professional work where established GPT-5.4 behavior is sufficient and Sol-level capability is unnecessary |
| [GPT-5.4 mini](https://developers.openai.com/api/docs/models/gpt-5.4-mini) | Strong compact model specifically positioned for coding, computer use, and subagents | **$0.75 / $0.075 / $4.50** | **0.188x / 0.225x** | Economical coding agents, parallel subagents, computer-use workflows, routine implementation, tests, and structured transformations |
| [GPT-5.4 nano](https://developers.openai.com/api/docs/models/gpt-5.4-nano) | Cheapest GPT-5.4-class model for simple, high-volume processing | **$0.20 / $0.02 / $1.25** | **0.05x / 0.063x** | Classification, ranking, extraction, routing, validation, metadata generation, and very simple subagent tasks |
| [GPT-5.3-Codex](https://developers.openai.com/api/docs/models/gpt-5.3-codex) | Older specialist optimized explicitly for agentic coding in Codex-like environments | **$1.75 / $0.175 / $14.00** | **0.438x / 0.70x** | Existing Codex-oriented coding pipelines, autonomous edit-test-debug loops, and coding-specific workloads; less compelling for broad research or general professional tasks |

## Practical Conclusions

- **Maximum-capability candidate:** GPT-6 Astra; evaluate whether task quality
  or fewer retries justify its 2.5x token rates versus Sol.
- **Lower-cost option for hard work:** GPT-5.6 Sol.
- **Best general cost/quality choice:** GPT-5.6 Terra.
- **Best economical modern GPT-5.6 agent:** GPT-5.6 Luna.
- **Lowest token-cost worker among these models:** GPT-5.6 Luna; it matches
  GPT-5.4 nano’s input rate and has a slightly lower output rate.
- **Older compact coding option:** GPT-5.4 mini, where existing evaluations
  justify its higher token cost than Luna.
- **GPT-5.3-Codex remains coding-specialized**, but GPT-5.6 Luna is cheaper on
  output and has a much larger context window. Evaluate Terra, Sol, or Astra when
  judgment and planning matter.
- **GPT-5.5 currently costs more per token than Sol** because Sol has promotional
  pricing through at least November 21, 2026. OpenAI does not state what Sol's
  price will be after the promotion. Continued GPT-5.5 use should therefore be
  justified by behavioral stability or pinned evaluations, rather than an
  assumption that an older model will be cheaper.

These ratios describe billed tokens, not total task cost. A cheaper model can
consume more tokens, require retries, or produce changes that need correction.

## GPT-6 Astra Details

Use the API model ID `gpt-6-astra`. It has a 1,050,000-token context window,
128,000-token maximum output, and April 30, 2026 knowledge cutoff. Text and
image inputs produce text output; native audio and video are unsupported.
See the [Astra model page](https://developers.openai.com/api/docs/models/gpt-6-astra).

Astra adds asynchronous tool calls, mid-turn steering over WebSockets, and
reasoning-effort changes that preserve the cached prompt prefix. Supported
API reasoning efforts are `low`, `medium`, `high`, `xhigh`, and `max`; `none`
and `minimal` are unsupported. Tool calling requires the Responses API even
though Chat Completions is also supported. Remove `temperature`, `top_p`,
and `top_logprobs` when adapting requests. See the
[official Astra guide](https://developers.openai.com/api/docs/guides/latest-model).

## Long-Context Pricing

For Astra and the GPT-5.6 tiers, prompts above 272K input tokens incur `2x`
input and cache rates and `1.5x` output rates for the full request. Astra’s
long-context input / cached input / output rates are therefore
**$20.00 / $2.00 / $75.00** per million tokens. Explicit cache writes cost
$12.50 per million tokens at short context and $25.00 at long context.
See [official API pricing](https://developers.openai.com/api/docs/pricing).

GPT-5.5 and GPT-5.4 also have long-context surcharges; consult their linked
model pages before estimating long-request costs. These API prices do not
represent Codex subscription usage allowances.
