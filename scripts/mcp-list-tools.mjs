#!/usr/bin/env node
// Speaks raw MCP (JSON-RPC 2.0 over stdio) to a server, does the initialize
// handshake, calls tools/list, and dumps the raw tool schemas as JSON.
// Usage: node mcp-list-tools.mjs <out.json> -- <server-cmd> [args...]

import { spawn } from "node:child_process";
import { writeFileSync } from "node:fs";

const args = process.argv.slice(2);
const sep = args.indexOf("--");
if (sep === -1) {
  console.error("usage: mcp-list-tools.mjs <out.json> -- <server-cmd> [args...]");
  process.exit(1);
}
const outFile = args[0];
const [cmd, ...cmdArgs] = args.slice(sep + 1);

const child = spawn(cmd, cmdArgs, { stdio: ["pipe", "pipe", "pipe"] });

let buf = "";
const pending = new Map();
let nextId = 1;

function send(method, params) {
  const id = nextId++;
  const msg = { jsonrpc: "2.0", id, method, params };
  child.stdin.write(JSON.stringify(msg) + "\n");
  return new Promise((resolve, reject) => {
    pending.set(id, { resolve, reject });
  });
}

child.stdout.on("data", (chunk) => {
  buf += chunk.toString();
  let idx;
  while ((idx = buf.indexOf("\n")) !== -1) {
    const line = buf.slice(0, idx).trim();
    buf = buf.slice(idx + 1);
    if (!line) continue;
    let msg;
    try {
      msg = JSON.parse(line);
    } catch {
      continue; // banner / non-JSON noise on stdout
    }
    if (msg.id && pending.has(msg.id)) {
      const { resolve, reject } = pending.get(msg.id);
      pending.delete(msg.id);
      if (msg.error) reject(new Error(JSON.stringify(msg.error)));
      else resolve(msg.result);
    }
  }
});

child.stderr.on("data", (chunk) => {
  process.stderr.write(chunk);
});

child.on("exit", (code) => {
  if (pending.size > 0) {
    console.error(`server exited (code ${code}) with ${pending.size} request(s) still pending`);
    process.exit(1);
  }
});

try {
  await send("initialize", {
    protocolVersion: "2024-11-05",
    capabilities: {},
    clientInfo: { name: "mcp-list-tools", version: "0.0.1" },
  });
  child.stdin.write(JSON.stringify({ jsonrpc: "2.0", method: "notifications/initialized" }) + "\n");
  const result = await send("tools/list", {});
  writeFileSync(outFile, JSON.stringify(result, null, 2));
  console.error(`wrote ${outFile}: ${result.tools?.length ?? 0} tools`);
} catch (e) {
  console.error("failed:", e.message);
  process.exitCode = 1;
} finally {
  child.stdin.end();
  child.kill();
}
