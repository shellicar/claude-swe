/**
 * Timing MITM: forwards to api.anthropic.com, records one JSONL line per request:
 * timestamps (start / first byte / last byte), model, conversation fingerprint,
 * message count, status, stop_reason, usage (tokens incl. cache + thinking).
 *
 * Attribution: conv = hash of the first user message, so parallel workers'
 * interleaved requests group back into per-instance conversations.
 *
 * Usage: node mitm/timing-mitm.mjs
 *   ANTHROPIC_BASE_URL=http://localhost:18899  (client side)
 *   PORT=...        override listen port        (default 18899)
 *   TIMING_LOG=...  override output path        (default mitm/api-timing.jsonl)
 */
import http from 'node:http';
import https from 'node:https';
import { createHash } from 'node:crypto';
import { appendFileSync } from 'node:fs';

const PORT = Number(process.env.PORT ?? 18899);
const TARGET = 'api.anthropic.com';
const LOG = process.env.TIMING_LOG ?? new URL('./api-timing.jsonl', import.meta.url).pathname;

let counter = 0;

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

// Non-streaming JSON responses only (litellm/mini do not stream). A streamed
// response still gets full timing; usage/stop_reason are simply left null.
const extractResult = (raw, streamed) => {
  try {
    if (streamed) return { stop_reason: null, usage: null };
    const j = JSON.parse(raw);
    return { stop_reason: j.stop_reason ?? null, usage: j.usage ?? null };
  } catch {
    return { stop_reason: null, usage: null };
  }
};

const server = http.createServer((req, res) => {
  let body = '';
  req.on('data', (c) => (body += c));
  req.on('end', () => {
    const n = ++counter;
    const meta = fingerprint(body);
    const tStart = Date.now();
    let tFirst = null;

    const headers = { ...req.headers, host: TARGET };
    delete headers['accept-encoding']; // identity response so we can parse it

    const fwd = https.request({ hostname: TARGET, path: req.url, method: req.method, headers }, (up) => {
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
          ...extractResult(raw, meta.stream),
        };
        appendFileSync(LOG, JSON.stringify(line) + '\n');
        console.log(`# ${n} ${meta.model ?? '?'} conv=${meta.conv ?? '?'} msgs=${meta.n_messages ?? '?'} ${up.statusCode} ttfb=${line.ttfb_ms}ms total=${line.total_ms}ms`);
      });
    });

    fwd.on('error', (e) => {
      appendFileSync(LOG, JSON.stringify({ n, ts: new Date(tStart).toISOString(), ...meta, status: null, error: e.message, total_ms: Date.now() - tStart }) + '\n');
      console.error(`# ${n} forward error:`, e.message);
      res.writeHead(502);
      res.end('Bad Gateway');
    });

    fwd.write(body);
    fwd.end();
  });
});

server.listen(PORT, () => {
  console.log(`# timing-mitm on :${PORT} -> ${TARGET}, logging to ${LOG}`);
});
