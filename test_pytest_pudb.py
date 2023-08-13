import re
import textwrap

import pexpect
import pytest

from pytest_pudb import ENTER_MESSAGE

pytest_plugins = "pytester"

HELP_MESSAGE = "\\?\\:help"
VARIABLES_TABLE = "V\x1b\\[0;30;47mariables:"


@pytest.fixture(autouse=True)
def pudb_xdg_home(tmp_path_factory):
    import os
    tmp_path = tmp_path_factory.mktemp("pudb")
    os.environ["XDG_CONFIG_HOME"] = str(tmp_path)

    tmp_path = tmp_path / "pudb"
    tmp_path.mkdir(parents=True, exist_ok=True)
    (tmp_path / "pudb.cfg").write_text(
        textwrap.dedent(
            """
            [pudb]
            prompt_on_quit = False
            # pudb/debugger.py:DebuggerUI#event_loop#WELCOME_LEVEL:2453
            seen_welcome = e999
            """
        )
    )

    yield


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


def test_pudb_avoid_double_prologue(testdir):
    p1 = testdir.makepyfile(
        """
        def test_1():
            test = []
            assert test[0]
    """
    )

    re_escape = re.escape(ENTER_MESSAGE).encode('utf-8')
    re_enter = re.compile(rb"\r\n>+ %s >+\r\n" % re_escape)  # \r\n instead of ^,$

    child = testdir.spawn_pytest("--pudb %s" % p1)
    child.expect(re_enter)
    child.expect("PuDB")
    child.expect(HELP_MESSAGE)
    # Check that traceback postmortem handled
    child.expect("PROCESSING EXCEPTION")
    child.expect(VARIABLES_TABLE)

    # Exit pudb
    child.write("q")
    ret = child.expect([re_enter, pexpect.EOF])

    if ret == 0:
        raise RuntimeError(f"pexpect found {re_enter!r} again!")
