"""Minimal example: ask Fidem who is behind a shop before paying. Standard library only.

    python check_shop.py shop.example
"""
import json
import sys
import urllib.parse
import urllib.request


def check_shop(domain: str) -> dict:
    url = 'https://fidemcheck.com/api/v1/tienda?dominio=' + urllib.parse.quote(domain)
    with urllib.request.urlopen(urllib.request.Request(url, headers={'User-Agent': 'fidem-example/1'}), timeout=40) as r:
        return json.load(r)


def summary(r: dict) -> str:
    if r.get('error'):
        return 'Not a valid domain.'
    if (r.get('listas_webs_peligrosas') or {}).get('codigo') == 'en_lista':
        return f"{r['dominio']} is on a phishing list. Do not pay."
    if r.get('nivel') == 'verificada_por_la_tienda':
        who = 'a sole trader' if r.get('tipo_titular') == 'autonomo' else 'a company'
        return f"{r['dominio']} is verified: run by {who}, proven to Fidem. {r.get('aviso_en') or r.get('aviso')}"
    emp = r.get('empresa') or {}
    return f"{r['dominio']}: public data only (company status: {emp.get('codigo')}). {r.get('aviso_en') or r.get('aviso')}"


if __name__ == '__main__':
    print(summary(check_shop(sys.argv[1] if len(sys.argv) > 1 else 'tienda-demo.fidemcheck.com')))
