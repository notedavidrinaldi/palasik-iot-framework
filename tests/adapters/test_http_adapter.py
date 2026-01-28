def test_http_adapter_init():
    from palasik.adapters.http.adapter import HTTPAdapter
    a = HTTPAdapter("http://localhost")
    assert a.endpoint == "http://localhost"
