from tennis_match import serve


def test_serve_balance():
    assert -36.25 <= serve.serve_balance(5, 50, 50, 50) <= -1.25
    assert -33.5 <= serve.serve_balance(1, 70, 70, 0) <= 1.5


def test_serve_in():
    assert round(serve.serve_in(5, 50), 4) == 0.8375
    assert round(serve.serve_in(1, 0), 4) == 0.93
    assert round(serve.serve_in(10, 100), 4) == 0.6


def test_ace():
    assert round(serve.ace(5, 50, 50, 50, 35), 4) == 0.0515
    assert round(serve.ace(1, 100, 0, 0, 35), 4) == 0.0813
    assert round(serve.ace(10, 100, 50, 30, 80), 4) == 0.145
