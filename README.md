# Fidem MCP: verify an online shop before your AI agent pays

[![Fidem MCP connector](https://glama.ai/mcp/connectors/com.fidemcheck/fidem/badges/score.svg)](https://glama.ai/mcp/connectors/com.fidemcheck/fidem)

A free, remote MCP server that tells an AI agent **who is behind an online shop** before it buys. No install, no API key.

```
https://fidemcheck.com/mcp
```

One tool, `consultar_tienda(dominio)`, takes a shop domain and returns facts, each with its source and date:

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
curl "https://fidemcheck.com/api/v1/tienda?dominio=shop.example"
```

A minimal Python agent tool is in [examples/check_shop.py](examples/check_shop.py).

## What to tell the user

- `nivel: verificada_por_la_tienda`: the shop proved to Fidem that it controls the domain and its company matches the register. `tipo_titular` says whether it is a company or a sole trader.
- `nivel: consulta_publica`: only public data. Say that the shop has not proved who runs it. That is not a sign of fraud.
- `listas_webs_peligrosas.codigo: en_lista`: the domain is on a phishing list. Do not pay.

## Limits, measured

Every month we run 50 large shops through the same check and publish the results, including what fails: [what an AI agent can know about an online shop](https://fidemcheck.com/what-ai-agents-can-know-about-a-shop.html). Limit: 300 lookups per hour per IP.

## For shops

Shops can prove who runs them by publishing a signed file. It is free for founding shops: [fidemcheck.com/for-shops](https://fidemcheck.com/for-shops.html).

## Registry

Listed in the official MCP Registry as `com.fidemcheck/fidem`.
