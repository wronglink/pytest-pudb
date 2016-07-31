import pudb


def test_set_trace_integration():
    import pudb
    pudb.set_trace()
    assert 1 == 2


def test_pudb_inteagration():
    assert 1 == 2
