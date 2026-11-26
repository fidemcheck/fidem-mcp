import json
import langchain_fidem as F


def test_espera_mientras_la_consulta_sigue():
    pedidas = []

    def pide(url, timeout):
        pedidas.append(url)
        if len(pedidas) == 1:
            return 200, {'lookup_status': 'in_progress', 'retry_after_seconds': 2}
        return 200, {'lookup_status': 'complete', 'decision': 'not_verified', 'identity_verified': False}

    esperas = []
    r = F.fidem_check(' shop.example ', pide=pide, dormir=esperas.append)
    assert pedidas[0] == 'https://fidemcheck.com/api/v1/shop?domain=shop.example'
    assert esperas == [2.0] and r['lookup_status'] == 'complete'


def test_deja_de_esperar():
    r = F.fidem_check('x.example', max_wait_seconds=1, pide=lambda u, t: (200, {'lookup_status': 'in_progress', 'retry_after_seconds': 30}),
                      dormir=lambda s: None)
    assert r['lookup_status'] == 'in_progress'


def test_limite():
    assert F.fidem_check('x.example', pide=lambda u, t: (429, {}))['error'] == 'rate_limited'


def test_solo_verified_cuenta():
    assert F.is_verified({'decision': 'verified', 'identity_verified': True})
    assert not F.is_verified({'decision': 'fictitious_demo', 'identity_verified': False})
    assert not F.is_verified(None)


def test_herramienta(monkeypatch):
    monkeypatch.setattr(F, '_pide', lambda u, t: (200, {'decision': 'fictitious_demo', 'identity_verified': False, 'lookup_status': 'complete'}))
    t = F.FidemCheckShop()
    assert t.name == 'check_shop' and 'identity_verified' in t.description
    assert json.loads(t.invoke({'domain': 'tienda-demo.fidemcheck.com'}))['decision'] == 'fictitious_demo'
