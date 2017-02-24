""" interactive debugging with PuDB, the Python Debugger. """
from __future__ import absolute_import
import pudb
import sys
from pudb.debugger import Debugger


def pytest_addoption(parser):
    group = parser.getgroup("general")
    group._addoption('--pudb', action="store_true", dest="usepudb", default=False,
                     help="start the PuDB debugger on errors.")


def pytest_configure(config):
    if config.getvalue("usepudb"):
        config.pluginmanager.register(PuDBInvoke(), 'pudbinvoke')

    pudb_wrapper = PuDBWrapper(config)

    old_set_trace = pudb.set_trace
    old_import = __builtins__['__import__']

    def pudb_b_import(name, *args, **kwargs):
        if name == 'pudb.b':
            return pudb_wrapper.set_trace(2)
        return old_import(name, *args, **kwargs)

    __builtins__['__import__'] = pudb_b_import

    def fin():
        pudb.set_trace = old_set_trace
        __builtins__['__import__'] = old_import

    pudb.set_trace = pudb_wrapper.set_trace
    config._cleanup.append(fin)


class PuDBWrapper(object):
    """ Pseudo PDB that defers to the real pudb. """
    pluginmanager = None
    config = None

    def __init__(self, config):
        self.config = config
        self.pluginmanager = config.pluginmanager

    def disable_io_capture(self):
        if self.pluginmanager is not None:
            capman = self.pluginmanager.getplugin("capturemanager")
            if capman:
                capman.suspendcapture(in_=True)
            tw = self.pluginmanager.getplugin("terminalreporter")._tw
            tw.line()
            tw.sep(">", "PuDB set_trace (IO-capturing turned off)")
            self.pluginmanager.hook.pytest_enter_pdb(config=self.config)

    def set_trace(self, depth=1):
        """ wrap pudb.set_trace, dropping any IO capturing. """
        self.disable_io_capture()
        dbg = Debugger()
        pudb.set_interrupt_handler()
        dbg.set_trace(sys._getframe(depth))


class PuDBInvoke(object):
    def pytest_exception_interact(self, node, call, report):
        capman = node.config.pluginmanager.getplugin("capturemanager")
        if capman:
            out, err = capman.suspendcapture(in_=True)
            sys.stdout.write(out)
            sys.stdout.write(err)
        _enter_pudb(node, call.excinfo, report)

    def pytest_internalerror(self, excrepr, excinfo):
        for line in str(excrepr).split("\n"):
            sys.stderr.write("INTERNALERROR> %s\n" %line)
            sys.stderr.flush()
        tb = _postmortem_traceback(excinfo)
        post_mortem(tb, excinfo)


def _enter_pudb(node, excinfo, rep):
    # XXX we re-use the TerminalReporter's terminalwriter
    # because this seems to avoid some encoding related troubles
    # for not completely clear reasons.
    tw = node.config.pluginmanager.getplugin("terminalreporter")._tw
    tw.line()
    tw.sep(">", "traceback")
    rep.toterminal(tw)
    tw.sep(">", "entering PuDB")
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
    dbg = Debugger()
    stack, i = dbg.get_stack(None, tb)
    dbg.reset()
    i = _find_last_non_hidden_frame(stack)
    dbg.interaction(stack[i][0], excinfo._excinfo)


def _find_last_non_hidden_frame(stack):
    i = max(0, len(stack) - 1)
    while i and stack[i][0].f_locals.get("__tracebackhide__", False):
        i -= 1
    return i
