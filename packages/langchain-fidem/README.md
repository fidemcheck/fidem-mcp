# langchain-fidem

Check which company operates an online shop before your agent pays. A [LangChain](https://python.langchain.com) tool for [Fidem](https://fidemcheck.com), free and without an API key.

For any shop domain, Fidem returns which company the website says it is and whether that company is in an official register (EU VIES, UK Companies House), the domain age, the first archived copy, the TLS certificate, the stated return window, whether the domain is on open phishing lists and whether its robots.txt lets AI agents in. Each fact comes with its source and date. When the shop has proved it controls the domain and represents its company, Fidem signs it and `decision` is `verified`.

## Install

```bash
pip install langchain-fidem
```

## Use

```python
from langchain_fidem import FidemCheckShop

tools = [FidemCheckShop()]          # give it to any LangChain or LangGraph agent
print(tools[0].invoke({"domain": "tienda-demo.fidemcheck.com"}))
```

Without an agent, as a plain function:

```python
from langchain_fidem import fidem_check, is_verified

answer = fidem_check("tienda-demo.fidemcheck.com")
print(answer["decision"], answer["identity_verified"])   # fictitious_demo False
print(is_verified(answer))                              # False
```

`tienda-demo.fidemcheck.com` is a fictitious shop that Fidem runs on its own subdomain. It always answers `fictitious_demo`, never `verified`.

## How to read the answer

Branch on `decision`. Only `verified`, with `identity_verified: True`, means the shop proved its identity and Fidem signed it. `is_verified(answer)` checks exactly that.

| `decision` | Meaning |
|---|---|
| `verified` | The shop proved the domain and its company, and Fidem signed it. |
| `domain_proven` | The shop proved the domain on the free plan, with no signed file and no proof of representation. |
| `in_review` | The shop proved the domain and Fidem is reviewing the company. |
| `not_verified` | No verification. This is not a sign of fraud: most shops have simply not done it. |
| `revoked`, `expired`, `invalid_file` | There was a verification and it no longer holds. |
| `fictitious_demo` | Fidem's fictitious example. Never pay it. |

For a company, `mvf_file.representation_proven: False` means Fidem signed it during the transition period, which is allowed until 1 January 2027.

The first lookup of a domain Fidem has never seen can come back with `lookup_status: "in_progress"`. The tool waits `retry_after_seconds` and asks again, for up to 45 seconds (`FidemCheckShop(max_wait_seconds=...)`), so the agent does not act on a partial answer.

If you prefer MCP, Fidem also runs a remote MCP server at `https://fidemcheck.com/mcp`, usable from LangChain with `langchain-mcp-adapters`: https://fidemcheck.com/langchain-check-online-shop.html

## More

- API and MCP server: https://fidemcheck.com/for-agents.html
- The signed file format (MVF, open standard): https://github.com/fidemcheck/mvf-spec
- Fidem gives no score and no buying advice, and says nothing about product quality or delivery.

MIT licence. Fidem, hola@fidemcheck.com.
