""" interactive debugging with PuDB, the Python Debugger. """
from __future__ import absolute_import
import pudb
import sys
import warnings


def pytest_addoption(parser):
    group = parser.getgroup("general")
    group._addoption('--pudb', action="store_true", dest="usepudb", default=False,
                     help="start the PuDB debugger on errors.")


def pytest_configure(config):
    pudb_wrapper = PuDBWrapper(config)

    if config.getvalue("usepudb"):
        config.pluginmanager.register(pudb_wrapper, 'pudb_wrapper')

    pudb_wrapper.mount()
    config._cleanup.append(pudb_wrapper.unmount)


class PuDBWrapper(object):
    """ Pseudo PDB that defers to the real pudb. """
    pluginmanager = None
    config = None

    def __init__(self, config):
        self.config = config
        self.pluginmanager = config.pluginmanager
        self._pudb_get_debugger = None

    def mount(self):
        self._pudb_get_debugger = pudb._get_debugger
        pudb._get_debugger = self._get_debugger

    def unmount(self):
        if self._pudb_get_debugger:
            pudb._get_debugger = self._pudb_get_debugger
            self._pudb_get_debugger = None

    def disable_io_capture(self):
        if self.pluginmanager is not None:
            capman = self.pluginmanager.getplugin("capturemanager")
            if capman:
                outerr = self._suspend_capture(capman, in_=True)
                if outerr:
                    out, err = outerr
                    sys.stdout.write(out)
                    sys.stdout.write(err)
            tw = self.pluginmanager.getplugin("terminalreporter")._tw
            tw.line()
            tw.sep(">", "entering PuDB (IO-capturing turned off)")
            self.pluginmanager.hook.pytest_enter_pdb(config=self.config)

    def _get_debugger(self, **kwargs):
        self.disable_io_capture()
        return self._pudb_get_debugger.__call__(**kwargs)

    def pytest_exception_interact(self, node, call, report):
        """
        Pytest plugin interface for exception handling
        https://docs.pytest.org/en/latest/reference.html#_pytest.hookspec.pytest_exception_interact
        """
        self.disable_io_capture()
        _enter_pudb(node, call.excinfo, report)

    def pytest_internalerror(self, excrepr, excinfo):
        """
        Pytest plugin interface for internal errors handling
        https://docs.pytest.org/en/latest/reference.html#_pytest.hookspec.pytest_internalerror
        """
        for line in str(excrepr).split("\n"):
            sys.stderr.write("INTERNALERROR> {}\n".format(line))
            sys.stderr.flush()
        tb = _postmortem_traceback(excinfo)
        post_mortem(tb, excinfo)

    def _suspend_capture(self, capman, *args, **kwargs):
        if hasattr(capman, 'suspendcapture'):
            # pytest changed the suspend capture API since v3.3.1
            # see: https://github.com/pytest-dev/pytest/pull/2801
            # TODO: drop this case after pytest v3.3.1+ is minimal required
            warnings.warn('You are using the outdated version of pytest. '
                          'The support for this version will be dropped in the future pytest-pudb versions.',
                          DeprecationWarning)
            return capman.suspendcapture(*args, **kwargs)

        if not hasattr(capman, 'snap_global_capture'):
            # pytest split suspend_global_capture into 2 calls since v3.7.3
            # see: https://github.com/pytest-dev/pytest/pull/3832
            # TODO: drop this case after pytest v3.7.3+ is minimal required
            return capman.suspend_global_capture(*args, **kwargs)

        capman.suspend_global_capture(*args, **kwargs)
        return capman.read_global_capture()


def _enter_pudb(node, excinfo, rep):
    tb = _postmortem_traceback(excinfo)
    post_mortem(tb, excinfo)
    rep._pdbshown = True
    return rep


def _postmortem_traceback(excinfo):
    # A doctest.UnexpectedException is not useful for post_mortem.
    # Use the underlying exception instead:
    from doctest import UnexpectedException
    if isinstance(excinfo.value, UnexpectedException):
        return excinfo.value.exc_info[2]
    else:
        return excinfo._excinfo[2]


def post_mortem(tb, excinfo):
    dbg = pudb._get_debugger()
    stack, i = dbg.get_stack(None, tb)
    dbg.reset()
    i = _find_last_non_hidden_frame(stack)
    dbg.interaction(stack[i][0], excinfo._excinfo)


def _find_last_non_hidden_frame(stack):
    i = max(0, len(stack) - 1)
    while i and stack[i][0].f_locals.get("__tracebackhide__", False):
        i -= 1
    return i
