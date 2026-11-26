import { test } from 'node:test';
import assert from 'node:assert/strict';
import { fidemCheck, isVerified, checkShop } from '../index.js';

const respuesta = (status, body) => ({ status, json: async () => body });

test('waits while the first lookup is in progress, then returns the full answer', async () => {
  const pedidas = [];
  const f = async (url) => {
    pedidas.push(url);
    return pedidas.length === 1
      ? respuesta(200, { domain: 'shop.example', lookup_status: 'in_progress', retry_after_seconds: 0.01 })
      : respuesta(200, { domain: 'shop.example', lookup_status: 'complete', decision: 'not_verified', identity_verified: false });
  };
  const r = await fidemCheck(' shop.example ', { fetch: f });
  assert.equal(pedidas.length, 2);
  assert.equal(pedidas[0], 'https://fidemcheck.com/api/v1/shop?domain=shop.example');
  assert.equal(r.lookup_status, 'complete');
});

test('gives up waiting after maxWaitSeconds and returns the partial answer', async () => {
  const f = async () => respuesta(200, { lookup_status: 'in_progress', retry_after_seconds: 30 });
  const r = await fidemCheck('slow.example', { fetch: f, maxWaitSeconds: 1 });
  assert.equal(r.lookup_status, 'in_progress');
});

test('rate limit is reported, not thrown', async () => {
  const r = await fidemCheck('x.example', { fetch: async () => respuesta(429, {}) });
  assert.equal(r.error, 'rate_limited');
});

test('only verified + identity_verified counts as verified; the demo never does', () => {
  assert.equal(isVerified({ decision: 'verified', identity_verified: true }), true);
  assert.equal(isVerified({ decision: 'fictitious_demo', identity_verified: false }), false);
  assert.equal(isVerified({ decision: 'domain_proven', identity_verified: false }), false);
  assert.equal(isVerified(null), false);
});

test('is a valid AI SDK tool', async () => {
  const t = checkShop({ fetch: async () => respuesta(200, { decision: 'fictitious_demo', identity_verified: false, lookup_status: 'complete' }) });
  assert.equal(typeof t.execute, 'function');
  assert.ok(t.inputSchema);
  assert.match(t.description, /identity_verified/);
  const r = await t.execute({ domain: 'tienda-demo.fidemcheck.com' }, { toolCallId: '1', messages: [] });
  assert.equal(r.decision, 'fictitious_demo');
});
