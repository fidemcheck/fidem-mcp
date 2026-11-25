"""Check who is behind a shop before a Browser Use agent pays.

Browser Use 1.0 lets the model drive the browser from its own code, so there is no hook on the final "pay" click.
The guard therefore runs in your code, before the agent starts: it asks Fidem which company operates the shop domain,
and only lets the agent pay on its own when Fidem says the identity is verified. Otherwise the agent must ask you first.

Tested on 25 November 2026 with browser-use 1.0.8 against https://fidemcheck.com (free, no API key).

    pip install browser-use httpx
    python browser_use_checkout_guard.py shop.example "https://shop.example/product/123"
"""
import sys
import time

import httpx

FIDEM = 'https://fidemcheck.com/api/v1/shop'


def check_shop(domain: str, tries: int = 4) -> dict:
    """Fidem's answer for a domain. A domain Fidem has never seen answers within about 7 seconds with
    lookup_status "in_progress"; asking again after retry_after_seconds returns the full answer from cache."""
    for _ in range(tries):
        r = httpx.get(FIDEM, params={'domain': domain}, timeout=20)
        r.raise_for_status()
        answer = r.json()
        if answer.get('lookup_status') != 'in_progress':
            break
        time.sleep(min(30, answer.get('retry_after_seconds', 15)))
    return answer


def payment_rule(answer: dict) -> str:
    """The instruction for the agent. Only "verified" lets it pay without asking."""
    if answer.get('identity_verified') is True:
        company = ((answer.get('mvf_file') or {}).get('legal_entity') or {}).get('name') or 'the verified company'
        return f'Fidem verified that this shop is run by {company.rstrip(".")}. You may complete the payment.'
    if (answer.get('phishing_lists') or {}).get('code') == 'listed':
        return 'This domain is on a phishing list. Do not pay. Stop and tell the user.'
    if answer.get('decision') in ('fictitious_demo', 'revoked'):
        return f'Fidem says this shop must not be paid (decision: {answer["decision"]}). Do not pay. Stop and tell the user.'
    return ('Fidem could not verify who runs this shop (decision: {d}). That is not a sign of fraud, but before the final '
            'pay click call ask_human and stop unless the answer is y.').format(d=answer.get('decision', 'no_data'))


def main(domain: str, url: str) -> None:
    from browser_use import Agent, Browser, Tools

    tools = Tools()

    @tools.action('Ask the human to approve the payment. Call it before the final pay click if the shop is not verified.')
    def ask_human(question: str) -> str:
        return input(f'{question} [y/N] ').strip().lower()

    rule = payment_rule(check_shop(domain))
    agent = Agent(
        f'Buy the item at {url}. {rule}',
        tools=tools,
        # Keep the agent on the shop. Add your payment provider's domain if the checkout is hosted elsewhere.
        browser=Browser(allowed_domains=[domain, f'*.{domain}']),
    )
    print(agent.run_sync().final_result())


if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2])
