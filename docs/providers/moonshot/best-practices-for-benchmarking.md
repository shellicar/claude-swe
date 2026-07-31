> ## Documentation Index
> Fetch the complete documentation index at: https://platform.kimi.ai/docs/llms.txt
> Use this file to discover all available pages before exploring further.

# Best Practices for Benchmarking

Benchmarking is an **engineering task** that needs stability and reproducibility. You'll be calling the model thousands of times; even tiny drifts in system setup or network latency can compromise result accuracy. Here's what we've learned to keep things reproducible and trustworthy.

**Quick notes**

* For any **unlisted** or **closed-source** benchmark:  set`temperature = 1.0`, `stream = true`, `top_p = 0.95`
* **Reasoning benchmarks**: `max_tokens = 128k`, and run at least **500–1000 samples** to get low variance (e.g. `AIME 2025`: 32 runs -> 30 × 32 = 960 questions)
* **Coding benchmarks**: `max_tokens = 256k`
* **Agentic task benchmarks:**
  * For multi-hop search: `max_tokens = 256k` + context management
  * Others: `max_tokens ≥ 16k–64k`

## K2.6 Models Benchmark Recommended Settings

| Benchmark Category | Benchmark | Temperature | Recommended max tokens | Recommended runs | Top-p | Others (e.g. test log) |
| --- | --- | --- | --- | --- | --- | --- |
| Multi-modal | MMMU-Pro | 1.0 | max tokens = 96k | 3 | top\_p=0.95 | thinking=`{"type": "enabled"}` |
| Multi-modal | MMMU-Pro w/ python | 1.0 | per step tokens = 64k;<br />total max tokens = 256k | 3 | top\_p=0.95 | Recommended max steps = 50<br />thinking=`{"type": "enabled"}` |
| Multi-modal | CharXiv (RQ) | 1.0 | max tokens = 96k | 3 | top\_p=0.95 | thinking=`{"type": "enabled"}` |
| Multi-modal | CharXiv (RQ) w/ python | 1.0 | per step tokens = 64k;<br />total max tokens = 256k | 3 | top\_p=0.95 | Recommended max steps = 50<br />thinking=`{"type": "enabled"}` |
| Multi-modal | MathVision | 1.0 | max tokens = 96k | 3 | top\_p=0.95 | thinking=`{"type": "enabled"}` |
| Multi-modal | MathVision w/ python | 1.0 | per step tokens = 64k;<br />total max tokens = 256k | 3 | top\_p=0.95 | Recommended max steps = 50<br />thinking=`{"type": "enabled"}` |
| Multi-modal | V\* w/ python | 1.0 | per step tokens = 64k;<br />total max tokens = 256k | 3 | top\_p=0.95 | Recommended max steps = 50<br />thinking=`{"type": "enabled"}` |
| Agent | HLE-Full w/ tools | 1.0 | per step tokens = 48k;<br />total max tokens = 256k | 1 | top\_p=0.95 | Recommended max steps = 300<br />thinking=`{"type": "enabled"}` |
| Agent | BrowseComp | 1.0 | per step tokens = 48k;<br />total max tokens = 256k | 1 | top\_p=0.95 | Recommended max steps = 300<br />thinking=`{"type": "enabled"}` |
| Agent | DeepSearchQA | 1.0 | per step tokens = 48k;<br />total max tokens = 256k | 1 | top\_p=0.95 | Recommended max steps = 300<br />thinking=`{"type": "enabled"}` |
| Agent | WideSearch | 1.0 | per step tokens = 48k;<br />total max tokens = 256k | 4 | top\_p=0.95 | Recommended max steps = 300<br />thinking=`{"type": "enabled"}` |
| Agent | Toolathlon | 1.0 | per step tokens = 48k;<br />total max tokens = 256k | 4 | top\_p=0.95 | Recommended max steps = 300<br />thinking=`{"type": "enabled"}` |
| Agent | MCPMark | 1.0 | per step tokens = 48k;<br />total max tokens = 256k | 4 | top\_p=0.95 | Recommended max steps = 300<br />thinking=`{"type": "enabled"}` |
| Agent | Claw Eval | 1.0 | per step tokens = 48k;<br />total max tokens = 256k | 4 | top\_p=0.95 | Recommended max steps = 300<br />thinking=`{"type": "enabled"}` |
| Agent | APEX-Agents | 1.0 | per step tokens = 48k;<br />total max tokens = 256k | 4 | top\_p=0.95 | Recommended max steps = 300<br />thinking=`{"type": "enabled"}` |
| Coding | Terminal-Bench 2.0 (Terminus-2) | 1.0 | max tokens = 256k | 3 | top\_p=0.95 | thinking=`{"type": "enabled"}` |
| Coding | SWE-Bench Pro | 1.0 | per step tokens = 32k;<br />total max tokens = 256k | 5 | top\_p=0.95 | Recommended max steps = 300<br />thinking=`{"type": "enabled"}` |
| Coding | SWE-Bench Multilingual | 1.0 | per step tokens = 32k;<br />total max tokens = 256k | 5 | top\_p=0.95 | Recommended max steps = 300<br />thinking=`{"type": "enabled"}` |
| Coding | SWE-Bench Verified | 1.0 | per step tokens = 32k;<br />total max tokens = 256k | 5 | top\_p=0.95 | Recommended max steps = 300<br />thinking=`{"type": "enabled"}` |
| Coding | SciCode | 1.0 | max tokens = 96k | 4 | top\_p=0.95 | thinking=`{"type": "enabled"}` |
| Coding | OJBench (python) | 1.0 | max tokens = 96k | 8 | top\_p=0.95 | thinking=`{"type": "enabled"}` |
| Coding | LiveCodeBench (v6) | 1.0 | max tokens = 96k | 1 | top\_p=0.95 | thinking=`{"type": "enabled"}` |
| Math | AIME 2026 | 1.0 | max tokens = 96k | 32 | top\_p=0.95 | thinking=`{"type": "enabled"}` |
| Math | HMMT 2026 (Feb) | 1.0 | max tokens = 96k | 32 | top\_p=0.95 | thinking=`{"type": "enabled"}` |
| Math | IMO-AnswerBench | 1.0 | max tokens = 96k | 4 | top\_p=0.95 | thinking=`{"type": "enabled"}` |
| Knowledge | HLE-Full | 1.0 | max tokens = 96k | 1 | top\_p=0.95 | thinking=`{"type": "enabled"}` |
| Knowledge | GPQA-Diamond | 1.0 | max tokens = 96k | 8 | top\_p=0.95 | thinking=`{"type": "enabled"}` |

## K2.5 Models Benchmark Recommended Settings

| Benchmark Category | Benchmark | Temperature | Recommended max tokens | Recommended runs | Top-p | Others (e.g. test log) |
| --- | --- | --- | --- | --- | --- | --- |
| Multi-modal | MMMU-Pro | 1.0 | max tokens = 64k | 3 | top\_p=0.95 | thinking=`{"type": "enabled"}` |
| Multi-modal | CharXiv (RQ) | 1.0 | max tokens = 64k | 3 | top\_p=0.95 | thinking=`{"type": "enabled"}` |
| Multi-modal | MathVision | 1.0 | max tokens = 64k | 3 | top\_p=0.95 | thinking=`{"type": "enabled"}` |
| Multi-modal | MathVista | 1.0 | max tokens = 64k | 3 | top\_p=0.95 | thinking=`{"type": "enabled"}` |
| Multi-modal | OCRBench | 1.0 | max tokens = 64k | 3 | top\_p=0.95 | thinking=`{"type": "enabled"}` |
| Multi-modal | ZeroBench | 1.0 | max tokens = 64k | 3 | top\_p=0.95 | thinking=`{"type": "enabled"}` |
| Multi-modal | WorldVQA | 1.0 | max tokens = 64k | 3 | top\_p=0.95 | thinking=`{"type": "enabled"}` |
| Multi-modal | InfoVQA (val) | 1.0 | max tokens = 64k | 3 | top\_p=0.95 | thinking=`{"type": "enabled"}` |
| Multi-modal | SimpleVQA | 1.0 | max tokens = 64k | 3 | top\_p=0.95 | thinking=`{"type": "enabled"}` |
| Multi-modal | ZeroBench w/ tools | 1.0 | max tokens = 64k | 3 | top\_p=0.95 | Recommended max steps = 30<br />thinking=`{"type": "enabled"}` |
| Code | SWE Series | 1.0 | per step tokens = 16k;<br />total max tokens = 256k | 5 | top\_p=0.95 | thinking=`{"type": "enabled"}` |
| Code | Lcb + OJBench | 1.0 | max tokens = 128k | 1 | top\_p=0.95 | thinking=`{"type": "enabled"}` |
| Code | TerminalBench | 1.0 | max tokens = 128k | 3 | top\_p=0.95 | thinking=`{"type": "enabled"}` |
| Reasoning | AIME2025 no tools | 1.0 | total max tokens = 96k | 32 | top\_p=0.95 | thinking=`{"type": "enabled"}` |
| Reasoning | AIME2025 w/ tools | 1.0 | per turn tokens = 96k;<br />total max tokens = 96k | 32 | top\_p=0.95 | thinking=`{"type": "enabled"}`<br />Recommended max steps = 120 |
| Reasoning | HLE no tools | 1.0 | max tokens = 96k | 1 | top\_p=0.95 | thinking=`{"type": "enabled"}` |
| Reasoning | HLE w/ tools | 1.0 | total max tokens = 128k;<br />per step tokens = 48k | 1 | top\_p=0.95 | thinking=`{"type": "enabled"}`<br />Recommended max steps = 120 |
| Reasoning | HLE heavy | 1.0 | total max tokens = 128k;<br />per step tokens = 48k | 1 | top\_p=0.95 | thinking=`{"type": "enabled"}`<br />Recommended max steps = 200<br />parallel n=8 |
| Reasoning | HMMT2025 no tools | 1.0 | max tokens = 96k | 32 | top\_p=0.95 | thinking=`{"type": "enabled"}` |
| Reasoning | HMMT2025 w/tools | 1.0 | per step tokens = 96k;<br />total tokens = 96k | 32 | top\_p=0.95 | thinking=`{"type": "enabled"}`<br />Recommended max steps = 120 |
| Reasoning | IMO-AnswerBench | 1.0 | max tokens = 96k | 3 | top\_p=0.95 | thinking=`{"type": "enabled"}` |
| Reasoning | GPQA-Diamond | 1.0 | max tokens = 96k | 8 | top\_p=0.95 | thinking=`{"type": "enabled"}` |
| Agentic Search Task | BrowseComp / BrowseComp-ZH / Seal-0 / Frames | 1.0 | per step tokens = 24k;<br />total max tokens = 256k | 4 | top\_p=0.95 | thinking=`{"type": "enabled"}`<br />Recommended max steps = 250<br />Recommend using a context management mechanism to prevent overly long context and ensure enough tool calls<br />Include today's date in the system prompt and let the model search when it is uncertain |
| Agentic Task | Tau | 1.0 | >=16k | 4 | top\_p=0.95 | thinking=`{"type": "enabled"}`<br />Recommended max steps = 100 |

For third-party providers, refer to Kimi Vendor Verifier (KVV) to choose high-accuracy services. Details: [https://kimi.com/blog/kimi-vendor-verifier.html](https://kimi.com/blog/kimi-vendor-verifier.html)

**Tool Use Compatibility**

When using tools, if the thinking parameter is set to `{"type": "enabled"}`, please note the following constraints to ensure model performance:

* `tool_choice` can only be set to "auto" or "none" (default is "auto") to avoid conflicts between reasoning content and the specified tool\_choice. Any other value will result in an error;
* During multi-step tool calling, you must keep the `reasoning_content` from the assistant message in the current turn's tool call within the context, otherwise an error will be thrown;
* The official builtin `$web_search` tool is temporarily incompatible with Kimi K2.5/K2.6 thinking mode, you can choose to disable thinking mode first and then use the `$web_search` tool.

You can refer to [Use Thinking Mode](/docs/guide/use-thinking-models) for correct usage of tool calling.

## K2-Thinking Series Models Benchmark Recommended Settings

| Category | Benchmark | Temperature | Max token | Suggested runs | Notes |
| --- | --- | --- | --- | --- | --- |
| Code | SWE | 0.7 (recommended)<br />1.0 (ok) | per step tokens = 16k;<br />total max token = 256k | 5 | |
| Code | Lcb + OJBench | 1.0 | max tokens = 128k | 1 | |
| Code | TerminalBench | 1.0 | max tokens = 128k | 3 | |
| Reasoning | AIME2025 no tools | 1.0 | total max tokens = 96k | 32 | |
| Reasoning | AIME2025 w/ tools | 1.0 | per step tokens = 48k;<br />total max tokens = 128k | 16 | max steps = 120 |
| Reasoning | HLE no tools | 1.0 | max tokens = 96k | 1 | |
| Reasoning | HLE w/ tools | 1.0 | total max tokens = 128k;<br />per step tokens = 48k | 1 | max steps = 120 |
| Reasoning | HLE heavy | 1.0 | total max tokens = 128k;<br />per step tokens = 48k | 1 | max steps = 200<br />parallel n=8 |
| Reasoning | HMMT2025 no tools | 1.0 | max tokens = 96k | 32 | |
| Reasoning | HMMT2025 w/tools | 1.0 | per step tokens = 96k;<br />total tokens = 96k | 32 | max steps = 120 |
| Reasoning | IMO-AnswerBench | 1.0 | max tokens = 96k | 3 | |
| Reasoning | GPQA-Diamond | 1.0 | max tokens = 96k | 8 | |
| Agentic Search Task | BrowseComp / BrowseComp-ZH / Seal-0 / Frames | 1.0 | per step tokens = 24k;<br />total max tokens = 256k | 4 | max steps = 250<br />Enable context management to prevent context overflow and ensure enough tool calls.<br />Include today's date in the system prompt, and tell the model to search when unsure. |
| Agentic Task | Tau | 0.0 | >=16k | 4 | max steps = 100 |

## API Recommendations & Notes

* **Use the official API:** some 3rd-party endpoints show noticeable accuracy drift.
* Use the recommended models for testing
  * For K2.6: use **`kimi-k2.6`** for testing
  * For K2.5: use **`kimi-k2.5`** for testing
  * For K2 series: use **`kimi-k2-thinking-turbo`** for faster inference
* **Must set:** `stream = true`
  * Non-streaming mode can lead to random mid-connection interruptions that are hard to control.
* **Current API default settings:**
  * Kimi K2.6:
    * default max\_tokens = 32768
    * default thinking = `{"type": "enabled", "keep": null}`
    * default temperature = 1.0
    * default top\_p = 0.95
    * default n = 1
    * default presence\_penalty = 0.0
    * default frequency\_penalty = 0.0
  * Kimi K2 Thinking:
    * default temp = 1.0
    * default max token = 64000
  * Kimi K2.5:
    * default max\_tokens = 32768
    * default thinking = `{"type": "enabled"}`
    * default temperature = 1.0
    * default top\_p = 0.95
    * default n = 1
    * default presence\_penalty = 0.0
    * default frequency\_penalty = 0.0
* **Timeouts:**
  * With `stream = false`, `api.moonshot.ai` timeout = **2 hours**, but some ISPs may terminate earlier.
  * So again we recommend you to set `stream = true`
* **Concurrency:**
  * Keep concurrency low to avoid rate limiting
* **Retry logic** is not optional:
  * handle overloaded
  * handle unexpected finish reason due to random server issues
  * handle errors due to complicated network issues

## FAQ

**Q1. Is the temperature setting consistent across models?**

**A.** No. Different model families use different recommended temperatures:

* k2.6 model: temperature = 1.0
* k2.5 model: temperature = 1.0
* k2-thinking series: temperature = 1.0
* k2 other series: temperature = 0.6

**Q2. Why use stream = true?**

**A.** Long outputs can take minutes. Idle TCP connections may be terminated by firewalls, load balancers, or NAT gateways. **Streaming keeps the connection alive** and significantly improves reliability. In production, requests with stream = false fail far more often than with stream = true.

**Q3. How much concurrency should I use?**

**A.** Your API account has specific rate limits (see [Recharge and Rate Limits](/docs/pricing/limits)). Start low. If you hit **HTTP 429** (rate limit), your concurrency is too high. **Accuracy > speed,** so tune concurrency to stay within limits.

**Q5. Why should I add retry?**

**A.** Even with streaming, requests can fail due to transient network issues. **Retry** on temporary faults (network jitter, server overload, rate limiting) to avoid avoidable failures.

**Q6. Why should multi-turn or multi-step tasks include full context and reasoning?**

**A.** The model needs full context to stay logically consistent. Without previous reasoning steps, later turns can go off track or produce incomplete answers.

## Contact Us

Hit any issues? Drop us an email at [**api-service@moonshot.ai**](mailto:api-service@moonshot.ai) with your logs. We'll take a look!
