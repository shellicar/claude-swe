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

const TARGET = 'api.anthropic.com';

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
} = {}) {
  let counter = 0;

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
          appendFileSync(timingLog, JSON.stringify(line) + '\n');
          console.log(`# ${n} ${meta.model ?? '?'} conv=${meta.conv ?? '?'} msgs=${meta.n_messages ?? '?'} ${up.statusCode} ttfb=${line.ttfb_ms}ms total=${line.total_ms}ms`);
        });
      });

      fwd.on('error', (e) => {
        appendFileSync(timingLog, JSON.stringify({ n, ts: new Date(tStart).toISOString(), ...meta, status: null, error: e.message, total_ms: Date.now() - tStart }) + '\n');
        console.error(`# ${n} forward error:`, e.message);
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
      console.log(`# timing-proxy on :${port} -> ${TARGET}, logging to ${timingLog}`);
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
