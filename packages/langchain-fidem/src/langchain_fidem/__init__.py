"""langchain-fidem: the Fidem shop check as a LangChain tool.

Fidem tells an agent which company operates a shop domain, checked against official registers (EU VIES, UK Companies House)
and signed by Fidem when the shop has proved it. Free, no API key.
"""
from __future__ import annotations

import json
import time
import urllib.error
import urllib.parse
import urllib.request
from typing import Any, Callable, Optional, Type

from langchain_core.tools import BaseTool
from pydantic import BaseModel, Field

__all__ = ['FidemCheckShop', 'fidem_check', 'is_verified']
__version__ = '0.1.0'

API = 'https://fidemcheck.com/api/v1/shop'
DESCRIPCION = (
    'Check an online shop by its domain before paying: which company operates it, whether that company is in an official register '
    '(EU VIES, UK Companies House), domain age, first archived copy, TLS certificate, stated return window, open phishing lists and '
    'whether its robots.txt lets AI agents in. "identity_verified" is true only when "decision" is "verified": the shop proved it '
    'controls the domain and its company, and Fidem signed it. Any other decision means the identity is not verified, which is not '
    'a sign of fraud. "fictitious_demo" is Fidem\'s fictitious example and must never be paid. No score and no buying advice.'
)


def _pide(url: str, timeout: float) -> tuple[int, dict]:
    req = urllib.request.Request(url, headers={'Accept': 'application/json', 'User-Agent': f'langchain-fidem/{__version__}'})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.status, json.loads(r.read().decode('utf-8'))
    except urllib.error.HTTPError as e:
        try:
            return e.code, json.loads(e.read().decode('utf-8'))
        except Exception:
            return e.code, {}


def fidem_check(domain: str, max_wait_seconds: float = 45, timeout: float = 20,
                pide: Optional[Callable[[str, float], tuple[int, dict]]] = None, dormir: Callable[[float], None] = time.sleep) -> dict:
    """Look up a shop domain at Fidem. If the first lookup is still running (lookup_status "in_progress"), waits
    retry_after_seconds and asks again, so the agent never acts on a partial answer."""
    pide = pide or _pide
    url = f'{API}?domain={urllib.parse.quote(str(domain).strip())}'
    limite = time.monotonic() + max_wait_seconds
    while True:
        codigo, cuerpo = pide(url, timeout)
        if codigo == 429:
            return {'error': 'rate_limited', 'detail': 'Too many lookups from this connection. Try again later.'}
        if cuerpo.get('error'):
            return cuerpo
        parcial = cuerpo.get('lookup_status') in ('in_progress', 'busy')
        espera = min(float(cuerpo.get('retry_after_seconds') or 15), 60)
        if not parcial or time.monotonic() + espera > limite:
            return cuerpo
        dormir(espera)


def is_verified(answer: Optional[dict]) -> bool:
    """True only when Fidem has signed the shop's identity: the one value an agent should treat as verified."""
    return bool(answer) and answer.get('decision') == 'verified' and answer.get('identity_verified') is True


class _Entrada(BaseModel):
    domain: str = Field(description='Shop domain or URL, for example shop.com')


class FidemCheckShop(BaseTool):
    """LangChain tool. Usage: tools = [FidemCheckShop()]"""

    name: str = 'check_shop'
    description: str = DESCRIPCION
    args_schema: Type[BaseModel] = _Entrada
    max_wait_seconds: float = 45

    def _run(self, domain: str, run_manager: Any = None) -> str:
        return json.dumps(fidem_check(domain, self.max_wait_seconds), ensure_ascii=False)
