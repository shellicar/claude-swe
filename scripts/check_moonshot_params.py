#!/usr/bin/env python3
"""Does litellm actually forward reasoning_effort to Moonshot?

`drop_params: true` removes anything the provider is not declared to support,
silently. A dropped effort parameter would leave every K3 leg running at the
model's default (max) while the run directories claim otherwise — a flat
effort curve that looks like a finding.
"""
import litellm

for model in ("kimi-k3", "kimi-k2.7-code"):
    params = litellm.get_supported_openai_params(
        model=model, custom_llm_provider="moonshot",
    )
    print(f"{model}: reasoning_effort supported = {'reasoning_effort' in params}")

# As an ordinary kwarg it is validated away; via extra_body it is forwarded
# verbatim. The second form is what orchestration/experiment.mjs must emit.
as_kwarg = litellm.utils.get_optional_params(
    model="kimi-k3",
    custom_llm_provider="moonshot",
    reasoning_effort="low",
    drop_params=True,
)
print("as a plain kwarg ->", as_kwarg)

via_extra_body = litellm.utils.get_optional_params(
    model="kimi-k3",
    custom_llm_provider="moonshot",
    extra_body={"reasoning_effort": "low"},
    drop_params=False,
)
print("via extra_body   ->", via_extra_body)

# Kimi documents max_completion_tokens as the output bound, but only
# max_tokens reaches the wire. Which of the two does litellm keep?
for kwargs in (
    {"max_completion_tokens": 32000},
    {"max_tokens": 32000},
    {"max_completion_tokens": 32000, "max_tokens": 32000},
):
    got = litellm.utils.get_optional_params(
        model="kimi-k3", custom_llm_provider="moonshot", drop_params=False, **kwargs,
    )
    print(f"{kwargs} -> {got}")
