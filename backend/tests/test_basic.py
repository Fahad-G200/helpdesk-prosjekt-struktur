def test_login_page(client):
    res = client.get("/login")
    assert res.status_code == 200

def test_register_page(client):
    res = client.get("/register")
    assert res.status_code == 200

def test_kb_page_requires_login(client):
    res = client.get("/kb")
    assert res.status_code in (302, 401)
