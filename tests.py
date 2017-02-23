def test_pudb_b_integration():
    import pudb.b
    assert 1 == 2


def test_set_trace_integration():
    import pudb
    pudb.set_trace()
    assert 1 == 2


def test_pudb_integration():
    assert 1 == 2
