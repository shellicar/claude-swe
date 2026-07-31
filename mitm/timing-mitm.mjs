/**
 * Timing proxy: forwards to api.anthropic.com and records one JSONL line per
 * request: timestamps (start / first byte / last byte), model, conversation
 * fingerprint, message count, status, stop_reason, usage (tokens incl. cache +
 * thinking).
 *
 * Attribution: conv = hash of the first user message, so parallel workers'
 * interleaved requests group back into per-instance conversations.
 *
 * It is an http.Server — nothing more — so run it IN-PROCESS from a Node
 * orchestrator rather than spawning a second node process:
 *
 *   import { startTimingProxy } from './mitm/timing-mitm.mjs';
 *   const proxy = await startTimingProxy({ port, timingLog });
 *   // point the run at proxy.baseUrl ...
 *   await proxy.stop();
 *
 * Or standalone (PORT / TIMING_LOG env):  node mitm/timing-mitm.mjs
 */
import http from 'node:http';
import https from 'node:https';
import { createHash } from 'node:crypto';
import { appendFileSync } from 'node:fs';
import { pathToFileURL } from 'node:url';

// The upstream host. The proxy itself stays provider-neutral — it forwards
// bytes and records `usage` raw, leaving the analysis to interpret whichever
// shape came back — so the host is the only thing a non-Anthropic contender
// changes. Default keeps every existing caller working unchanged.
const TARGET = process.env.TIMING_PROXY_TARGET ?? 'api.anthropic.com';

const fingerprint = (body) => {
  try {
    const j = JSON.parse(body);
    const first = (j.messages ?? []).find((m) => m.role === 'user');
    return {
      model: j.model,
      stream: Boolean(j.stream),
      n_messages: (j.messages ?? []).length,
      // Hash only the text of the first user message: cache_control markers move
      // between requests and must not change the conversation identity.
      conv: createHash('sha256')
        .update(typeof first?.content === 'string' ? first.content : (first?.content ?? []).map((b) => b.text ?? '').join('\n'))
        .digest('hex')
        .slice(0, 12),
    };
  } catch {
    return { model: null, stream: false, n_messages: null, conv: null };
  }
};

/** Splits an SSE body into its `data:` payloads. Frames end at a blank line,
 * which may be LF or CRLF; `data:` may repeat within one frame and a leading
 * space after the colon is not part of the value. Comments (`:`) and the
 * OpenAI `[DONE]` sentinel carry nothing. */
const sseData = (raw) => {
  const out = [];
  for (const block of raw.split(/\r?\n\r?\n/)) {
    const lines = [];
    for (const line of block.split(/\r?\n/)) {
      if (!line.startsWith('data:')) continue;
      const v = line.slice(5);
      lines.push(v.startsWith(' ') ? v.slice(1) : v);
    }
    const data = lines.join('\n');
    if (data && data !== '[DONE]') out.push(data);
  }
  return out;
};

/** Usage from a streamed response. The two wire shapes report it differently:
 * Anthropic SPLITS it — input and cache counts arrive on `message_start`,
 * output tokens and stop_reason on `message_delta` — while OpenAI-shaped
 * providers put a complete `usage` object on the final chunk. Reconstructing
 * both keeps the timing log identical whether or not the leg streamed. */
const fromStream = (raw) => {
  let usage = null;
  let stop_reason = null;
  for (const data of sseData(raw)) {
    let e;
    try {
      e = JSON.parse(data);
    } catch {
      continue;
    }
    if (e.type === 'message_start' && e.message?.usage) {
      usage = { ...e.message.usage };
    } else if (e.type === 'message_delta') {
      stop_reason = e.delta?.stop_reason ?? stop_reason;
      if (e.usage) usage = { ...(usage ?? {}), ...e.usage };
    } else if (e.usage) {
      usage = { ...(usage ?? {}), ...e.usage }; // OpenAI-shaped final chunk
    }
    stop_reason = e.choices?.[0]?.finish_reason ?? stop_reason;
  }
  return { stop_reason, usage };
};

export const extractResult = (raw, streamed) => {
  try {
    if (streamed) return fromStream(raw);
    const j = JSON.parse(raw);
    // stop_reason is Anthropic's name for it; OpenAI-shaped providers put the
    // same fact in choices[].finish_reason.
    return {
      stop_reason: j.stop_reason ?? j.choices?.[0]?.finish_reason ?? null,
      usage: j.usage ?? null,
    };
  } catch {
    return { stop_reason: null, usage: null };
  }
};

/**
 * Create the proxy server and resolve once it is listening. Rejects if the port
 * is already taken (EADDRINUSE) — a second run sharing one proxy scrambles
 * per-instance attribution (learned 2026-06-10). One proxy per run, or none.
 *
 * @returns {Promise<{ baseUrl: string, port: number, server: import('node:http').Server, stop: () => Promise<void> }>}
 */
export function startTimingProxy({
  port = Number(process.env.PORT ?? 18899),
  timingLog = process.env.TIMING_LOG ?? new URL('./api-timing.jsonl', import.meta.url).pathname,
  label,
  // Per-leg, because parallel legs may target different providers.
  target = TARGET,
} = {}) {
  let counter = 0;
  // Console prefix so parallel proxies' lines are attributable to their leg.
  const pre = label ? `[${label}] ` : '';

  const server = http.createServer((req, res) => {
    let body = '';
    req.on('data', (c) => (body += c));
    req.on('end', () => {
      const n = ++counter;
      const meta = fingerprint(body);
      const tStart = Date.now();
      let tFirst = null;

      const headers = { ...req.headers, host: target };
      delete headers['accept-encoding']; // identity response so we can parse it

      const fwd = https.request({ hostname: target, path: req.url, method: req.method, headers }, (up) => {
        res.writeHead(up.statusCode, up.headers);
        let raw = '';
        up.on('data', (c) => {
          if (tFirst === null) tFirst = Date.now();
          raw += c;
          res.write(c);
        });
        up.on('end', () => {
          res.end();
          const tEnd = Date.now();
          const line = {
            n,
            ts: new Date(tStart).toISOString(),
            ...meta,
            status: up.statusCode,
            ttfb_ms: tFirst === null ? null : tFirst - tStart,
            total_ms: tEnd - tStart,
            // Trust the response, not the request: a provider may stream when
            // asked to, or not, and the content-type is what actually arrived.
            ...extractResult(raw, (up.headers['content-type'] ?? '').includes('text/event-stream')),
          };
          appendFileSync(timingLog, JSON.stringify(line) + '\n');
          console.log(`${pre}# ${n} ${meta.model ?? '?'} conv=${meta.conv ?? '?'} msgs=${meta.n_messages ?? '?'} ${up.statusCode} ttfb=${line.ttfb_ms}ms total=${line.total_ms}ms`);
        });
      });

      fwd.on('error', (e) => {
        appendFileSync(timingLog, JSON.stringify({ n, ts: new Date(tStart).toISOString(), ...meta, status: null, error: e.message, total_ms: Date.now() - tStart }) + '\n');
        console.error(`${pre}# ${n} forward error:`, e.message);
        res.writeHead(502);
        res.end('Bad Gateway');
      });

      fwd.write(body);
      fwd.end();
    });
  });

  return new Promise((resolve, reject) => {
    server.once('error', reject); // e.g. EADDRINUSE
    server.listen(port, () => {
      server.off('error', reject);
      console.log(`${pre}# timing-proxy on :${port} -> ${target}, logging to ${timingLog}`);
      resolve({
        baseUrl: `http://localhost:${port}`,
        port,
        server,
        stop: () => new Promise((done) => server.close(() => done())),
      });
    });
  });
}

// Standalone: `node mitm/timing-mitm.mjs`
if (process.argv[1] && import.meta.url === pathToFileURL(process.argv[1]).href) {
  startTimingProxy().catch((e) => {
    console.error('timing-proxy failed to start:', e.message);
    process.exit(1);
  });
}
