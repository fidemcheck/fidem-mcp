# Fidem MCP: verify an online shop before your AI agent pays

[![Fidem MCP connector](https://glama.ai/mcp/connectors/com.fidemcheck/fidem/badges/score.svg)](https://glama.ai/mcp/connectors/com.fidemcheck/fidem)

A free, remote MCP server that tells an AI agent **who is behind an online shop** before it buys. No install, no API key.

```
https://fidemcheck.com/mcp
```

Two tools with the same data: `check_shop(domain)`, with English field names, and the original `consultar_tienda(dominio)`, with Spanish field names. Each takes a shop domain and returns facts, each with its source and date:

| Fact | Source |
|---|---|
| Whether the shop publishes a signed verification file and the signature is valid | [MVF open standard](https://github.com/fidemcheck/mvf-spec), Ed25519 |
| Which company the site claims to be and whether it is in the official register | VIES (EU), Companies House (UK) |
| How long the domain has existed | RDAP |
| First archived copy of the site | Internet Archive |
| The TLS certificate, and the organisation it names if it is OV/EV | The site itself |
| The return window the shop promises, with the sentence it comes from | The site itself |
| Whether the domain is on an open list of active phishing sites | Phishing.Database |
| Whether the shop's `robots.txt` lets AI agents in (ChatGPT, Claude, Perplexity), and which ones it blocks | The site's `robots.txt` |

It does not rate products, deliveries or service, and it never turns a missing fact into an accusation: **an unverified shop is not a fraudulent shop.**

## Connect it

**Claude Desktop, Claude Code, Cursor, Windsurf and any client that reads `mcpServers`:**

```json
{
  "mcpServers": {
    "fidem": { "url": "https://fidemcheck.com/mcp" }
  }
}
```

**VS Code** (`.vscode/mcp.json`):

```json
{
  "servers": {
    "fidem": { "type": "http", "url": "https://fidemcheck.com/mcp" }
  }
}
```

**Claude Code from the terminal:**

```
claude mcp add --transport http fidem https://fidemcheck.com/mcp
```

**No MCP? Call the API.** Same answer as JSON, described in [OpenAPI 3.1](https://fidemcheck.com/openapi.json):

```
curl "https://fidemcheck.com/api/v1/shop?domain=shop.example"
```

## Packages

If you would rather call it as a tool than connect the MCP server, the same check comes as a package. Both wait on their own while the first lookup of a new domain is still running, so the agent never acts on a partial answer.

- **Vercel AI SDK:** [`@fidemcheck/ai-sdk`](packages/ai-sdk), with `checkShop()`, `fidemCheck()` and `isVerified()`.
- **LangChain:** [`langchain-fidem`](packages/langchain-fidem), with `FidemCheckShop`, `fidem_check()` and `is_verified()`.

They are not on npm and PyPI yet. Until they are, install them from this repository.

## Examples and framework guides

- [examples/check_shop.py](examples/check_shop.py): a minimal Python agent tool.
- [examples/browser_use_checkout_guard.py](examples/browser_use_checkout_guard.py): Browser Use 1.0. Checks the shop before the agent starts and only lets it pay on its own when the identity is verified.
- Guides with tested code: [LangChain](https://fidemcheck.com/langchain-check-online-shop.html), [OpenAI Agents SDK](https://fidemcheck.com/openai-agents-sdk-check-online-shop.html), [Vercel AI SDK](https://fidemcheck.com/vercel-ai-sdk-check-online-shop.html).

## What to tell the user

Branch on `decision`. It is the same in the MCP tool, the REST API and the [reference checker](https://github.com/fidemcheck/mvf-spec).

| `decision` | What it means | What the agent should do |
|---|---|---|
| `verified` | The company proved control of the domain and was checked against the official register. The only value where `identity_verified` is `true` | Pay without asking, if your policy allows it |
| `domain_proven` | The shop proved the domain on the free plan, without a signed file | Show the user the facts and ask |
| `in_review` | The shop proved the domain and its company is being checked | Show the facts and ask |
| `not_verified` | No verification. Most shops have none yet, so this is not a sign of fraud | Show the facts and ask |
| `revoked`, `expired`, `invalid_file` | A verification existed and no longer holds | Ask, and say why |
| `fictitious_demo` | Fidem's own example shop | Never pay |
| `no_data` | The check could not finish | Ask |

If `phishing_lists.code` is `listed`, the domain is on an open list of active phishing sites. Do not pay.

The first lookup of a domain Fidem has never seen answers within about 7 seconds. If the full check is still running you get `lookup_status: "in_progress"` and `retry_after_seconds: 15`, and the next call returns the full answer from cache.

## Limits, measured

On 24 November 2026 we ran 1,000 shops from 14 countries through the same check and published the results, including what fails: [what an AI agent can know about an online shop](https://fidemcheck.com/what-ai-agents-can-know-about-a-shop.html). Limit: 300 lookups per hour per IP.

## For shops

Shops can prove who runs them by publishing a signed file. It is free for founding shops: [fidemcheck.com/for-shops](https://fidemcheck.com/for-shops.html).

## Registry

Listed in the official MCP Registry as `com.fidemcheck/fidem`.
