// The proxy's job is to record what came back regardless of wire shape, so
// the parser is tested against both: Anthropic splits usage across
// message_start and message_delta; OpenAI-shaped providers put it whole on a
// final chunk.
import assert from 'node:assert/strict';
import test from 'node:test';

import { extractResult } from './timing-mitm.mjs';

const anthropicStream = [
  'event: message_start',
  'data: {"type":"message_start","message":{"usage":{"input_tokens":4,"cache_read_input_tokens":9472,"cache_creation_input_tokens":101}}}',
  '',
  'event: ping',
  'data: {"type":"ping"}',
  '',
  'event: content_block_delta',
  'data: {"type":"content_block_delta","delta":{"text":"hi"}}',
  '',
  'event: message_delta',
  'data: {"type":"message_delta","delta":{"stop_reason":"tool_use"},"usage":{"output_tokens":148}}',
  '',
].join('\n');

const openaiStream = [
  'data: {"choices":[{"delta":{"content":"hi"},"finish_reason":null}]}',
  '',
  'data: {"choices":[{"delta":{},"finish_reason":"tool_calls"}],"usage":{"prompt_tokens":9873,"completion_tokens":148,"cached_tokens":9472}}',
  '',
  'data: [DONE]',
  '',
].join('\r\n');

test('anthropic stream: usage is reassembled from both events', () => {
  const expected = {
    stop_reason: 'tool_use',
    usage: {
      input_tokens: 4,
      cache_read_input_tokens: 9472,
      cache_creation_input_tokens: 101,
      output_tokens: 148,
    },
  };

  const actual = extractResult(anthropicStream, true);

  assert.deepEqual(actual, expected);
});

test('openai stream: usage comes off the final chunk, CRLF framed', () => {
  const expected = {
    stop_reason: 'tool_calls',
    usage: { prompt_tokens: 9873, completion_tokens: 148, cached_tokens: 9472 },
  };

  const actual = extractResult(openaiStream, true);

  assert.deepEqual(actual, expected);
});

test('non-streamed responses are unchanged', () => {
  const body = JSON.stringify({ stop_reason: 'end_turn', usage: { input_tokens: 2 } });
  const expected = { stop_reason: 'end_turn', usage: { input_tokens: 2 } };

  const actual = extractResult(body, false);

  assert.deepEqual(actual, expected);
});

test('a truncated stream yields what arrived, not an exception', () => {
  const truncated = 'event: message_start\ndata: {"type":"message_start","message":{"usage":{"input_tokens":4}}}\n\nevent: content_bl';
  const expected = { stop_reason: null, usage: { input_tokens: 4 } };

  const actual = extractResult(truncated, true);

  assert.deepEqual(actual, expected);
});
