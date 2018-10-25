pytest_plugins = "pytester"

HELP_MESSAGE = "\\?\\:help"
VARIABLES_TABLE = "V\x1b\\[0;30;47mariables:"


def test_pudb_interaction(testdir):
    p1 = testdir.makepyfile("""
        def test_1():
            assert 0 == 1
    """)
    child = testdir.spawn_pytest("--pudb %s" % p1)
    child.expect("PuDB")
    child.expect(HELP_MESSAGE)
    # Check that traceback postmortem handled
    child.expect("PROCESSING EXCEPTION")
    child.expect(VARIABLES_TABLE)
    child.sendeof()


def test_pudb_set_trace_integration(testdir):
    p1 = testdir.makepyfile("""
        def test_1():
            import pudb
            pudb.set_trace()
            assert 1
    """)
    child = testdir.spawn_pytest(p1)
    child.expect("PuDB")
    child.expect(HELP_MESSAGE)
    child.expect(VARIABLES_TABLE)
    child.sendeof()


def test_pu_db_integration(testdir):
    p1 = testdir.makepyfile("""
        def test_1():
            import pudb
            pu.db
            assert 1
    """)
    child = testdir.spawn_pytest(p1)
    child.expect("PuDB")
    child.expect(HELP_MESSAGE)
    child.expect(VARIABLES_TABLE)
    child.sendeof()


def test_pudb_b_integration(testdir):
    p1 = testdir.makepyfile("""
        def test_1():
            import pudb.b
            assert 1
    """)
    child = testdir.spawn_pytest(p1)
    child.expect("PuDB")
    child.expect(HELP_MESSAGE)
    child.expect(VARIABLES_TABLE)
    child.sendeof()
