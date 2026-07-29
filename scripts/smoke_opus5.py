#!/usr/bin/env python3
"""One-shot smoke test: does litellm accept anthropic/claude-opus-5 at all?
Minimal token spend, no swebench harness involved.
"""
import os
import sys

# Minimal .env loader — no python-dotenv dependency needed.
env_path = os.path.join(os.path.dirname(__file__), "..", ".env")
with open(env_path) as f:
    for line in f:
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, v = line.split("=", 1)
        os.environ[k] = v

import litellm

import time
import httpx

REQUEST_LOG = os.path.join(os.path.dirname(__file__), "..", "opus5_request.log")
CURL_LOG = os.path.join(os.path.dirname(__file__), "..", "opus5_request.curl.sh")
_log_lines = []
_curl_lines = []

def _log(s):
    _log_lines.append(s)

import shlex

def _write_curl(request):
    # UNREDACTED — this file is for the SC to run himself on his own
    # machine to reproduce the exact request; never echoed back in chat.
    parts = ["curl", "-i", "-X", request.method, shlex.quote(str(request.url))]
    for k, v in request.headers.items():
        if k.lower() in ("host", "content-length", "accept-encoding", "connection"):
            continue  # curl sets these itself
        parts += ["-H", shlex.quote(f"{k}: {v}")]
    try:
        body = request.content.decode("utf-8")
        parts += ["-d", shlex.quote(body)]
    except Exception:
        pass
    _curl_lines.append(" \\\n  ".join(parts))

_orig_send = httpx.Client.send
def _logging_send(self, request, *a, **kw):
    if "api.anthropic.com" in str(request.url):
        _write_curl(request)
    _log(f"=== REQUEST {request.method} {request.url} ===")
    for k, v in request.headers.items():
        if k.lower() == "authorization":
            v = v[:20] + "...REDACTED..." + v[-6:]
        if k.lower() == "x-api-key":
            v = v[:10] + "...REDACTED"
        _log(f"{k}: {v}")
    try:
        body = request.content.decode("utf-8", errors="replace")
    except Exception:
        body = "<binary>"
    _log(f"--- body ---\n{body}\n")
    resp = _orig_send(self, request, *a, **kw)
    _log(f"=== RESPONSE {resp.status_code} ===")
    for k, v in resp.headers.items():
        _log(f"{k}: {v}")
    try:
        resp.read()
        _log(f"--- response body ---\n{resp.text}\n")
    except Exception as e:
        _log(f"<could not read response body: {e}>")
    return resp
httpx.Client.send = _logging_send

_orig_asend = httpx.AsyncClient.send
async def _logging_asend(self, request, *a, **kw):
    _log(f"=== ASYNC REQUEST {request.method} {request.url} ===")
    for k, v in request.headers.items():
        if k.lower() == "authorization":
            v = v[:20] + "...REDACTED..." + v[-6:]
        if k.lower() == "x-api-key":
            v = v[:10] + "...REDACTED"
        _log(f"{k}: {v}")
    try:
        body = request.content.decode("utf-8", errors="replace")
    except Exception:
        body = "<binary>"
    _log(f"--- body ---\n{body}\n")
    resp = await _orig_asend(self, request, *a, **kw)
    _log(f"=== ASYNC RESPONSE {resp.status_code} ===")
    for k, v in resp.headers.items():
        _log(f"{k}: {v}")
    try:
        await resp.aread()
        _log(f"--- response body ---\n{resp.text}\n")
    except Exception as e:
        _log(f"<could not read response body: {e}>")
    return resp
httpx.AsyncClient.send = _logging_asend

MODELS = ["anthropic/claude-sonnet-4-6"]

for model in MODELS:
    print(f"--- {model} ---")
    time.sleep(3)
    try:
        resp = litellm.completion(
            model=model,
            messages=[{"role": "user", "content": "Reply with exactly: ok"}],
            max_tokens=8,
            # litellm 1.93.0's automatic OAuth-header handling isn't wired
            # into the plain completion() path for an sk-ant-oat* token —
            # confirmed by capturing the actual wire request, which had
            # neither header. Send them explicitly until that's fixed
            # upstream or the vendored fork patches it.
            extra_headers={
                "anthropic-beta": "oauth-2025-04-20",
                "anthropic-dangerous-direct-browser-access": "true",
            },
        )
        print("OK:", resp.choices[0].message.content)
        print("model returned:", resp.model)
        try:
            cost = litellm.completion_cost(completion_response=resp)
            print("cost: $%.6f" % cost)
        except Exception as e:
            print("cost lookup failed:", e)
    except Exception as e:
        print("ERROR:", type(e).__name__, str(e)[:500])

with open(REQUEST_LOG, "w") as f:
    f.write("\n".join(_log_lines))
print(f"\nwrote {REQUEST_LOG}")
with open(CURL_LOG, "w") as f:
    f.write("#!/bin/sh\n" + "\n\n".join(_curl_lines) + "\n")
os.chmod(CURL_LOG, 0o700)
print(f"wrote {CURL_LOG} (unredacted, run it yourself)")
