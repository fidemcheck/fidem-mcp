// @fidemcheck/ai-sdk: the Fidem shop check as a Vercel AI SDK tool.
// Fidem tells an agent which company operates a shop domain, checked against official registers (EU VIES, UK Companies House)
// and signed by Fidem when the shop has proved it. Free, no API key.
import { tool } from 'ai';
import { z } from 'zod';

const API = 'https://fidemcheck.com/api/v1/shop';
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

/**
 * Look up a shop domain at Fidem. The first lookup of a domain Fidem has never seen can answer with
 * lookup_status "in_progress": this waits retry_after_seconds and asks again, so the agent never acts on a partial answer.
 */
export async function fidemCheck(domain, { fetch: f = globalThis.fetch, maxWaitSeconds = 45, signal } = {}) {
  const url = `${API}?domain=${encodeURIComponent(String(domain).trim())}`;
  const limit = Date.now() + maxWaitSeconds * 1000;
  for (;;) {
    const r = await f(url, { headers: { Accept: 'application/json', 'User-Agent': 'fidemcheck-ai-sdk/0.1.0' }, signal });
    if (r.status === 429) return { error: 'rate_limited', detail: 'Too many lookups from this connection. Try again later.' };
    const body = await r.json();
    if (body.error) return body;
    const partial = body.lookup_status === 'in_progress' || body.lookup_status === 'busy';
    const wait = Math.min(Number(body.retry_after_seconds) || 15, 60) * 1000;
    if (!partial || Date.now() + wait > limit) return body;
    await sleep(wait);
  }
}

/** True only when Fidem has signed the shop's identity: the one value an agent should treat as verified. */
export const isVerified = (answer) => Boolean(answer && answer.decision === 'verified' && answer.identity_verified === true);

/**
 * The AI SDK tool. Usage:
 *   import { checkShop } from '@fidemcheck/ai-sdk';
 *   const result = await generateText({ model, tools: { checkShop: checkShop() }, prompt });
 */
export function checkShop(options = {}) {
  return tool({
    description:
      'Check an online shop by its domain before paying: which company operates it, whether that company is in an official register ' +
      '(EU VIES, UK Companies House), domain age, first archived copy, TLS certificate, stated return window, open phishing lists and ' +
      'whether its robots.txt lets AI agents in. "identity_verified" is true only when "decision" is "verified": the shop proved it ' +
      'controls the domain and its company, and Fidem signed it. Any other decision means the identity is not verified, which is not ' +
      'a sign of fraud. "fictitious_demo" is Fidem\'s fictitious example and must never be paid. No score and no buying advice.',
    inputSchema: z.object({ domain: z.string().describe('Shop domain or URL, for example shop.com') }),
    execute: async ({ domain }, { abortSignal } = {}) => fidemCheck(domain, { ...options, signal: abortSignal }),
  });
}

export default checkShop;
