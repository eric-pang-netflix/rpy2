import atexit
import collections
import os
import sys
import warnings
from rpy2.situation import (r_home_from_subprocess,
                            r_home_from_registry,
                            get_r_home, 
                            assert_python_version)

class RRuntimeWarning(RuntimeWarning):
    pass

assert_python_version()

def _load_r_dll(r_home):
    """Load the R.DLL matching Python's bitness.

    Add directories containing R DLLs to the PATH environment variable.

    """
    import ctypes
    r_arch = ('i386', 'x64')[sys.maxsize > 2**32]
    r_mod = os.path.join(r_home, 'modules', r_arch)
    r_bin = os.path.join(r_home, 'bin', r_arch)
    r_dll = os.path.join(r_bin, 'R.dll')
    if not os.path.exists(r_dll):
        raise RuntimeError("Unable to locate R.dll at %s" % r_dll)
    if r_bin not in os.environ.get('PATH'):
        os.environ['PATH'] = ';'.join((os.environ.get('PATH'), r_bin, r_mod))
    ctypes.CDLL(r_dll)

R_HOME = get_r_home()

if not R_HOME:
    raise RuntimeError("""The R home directory could not be determined.

    Try to install R <https://www.r-project.org/>,
    set the R_HOME environment variable to the R home directory, or
    add the directory of the R interpreter to the PATH environment variable.
    """)

if not os.environ.get("R_HOME"):
    os.environ['R_HOME'] = R_HOME

if sys.platform == 'win32':
    _load_r_dll(R_HOME)


from rpy2.rinterface._rinterface import (baseenv,
                                         emptyenv,
                                         endr,
                                         initr,
                                         is_initialized,
                                         get_choosefile,
                                         get_cleanup,
                                         get_flushconsole,
                                         get_initoptions,
                                         get_readconsole,
                                         get_resetconsole,
                                         get_showfiles,
                                         get_showmessage,
                                         get_writeconsole_regular,
                                         get_writeconsole_warnerror,
                                         globalenv,
                                         initoptions,
                                         parse,
                                         process_revents,
                                         protected_rids,
                                         python_type_tag,
                                         set_choosefile,
                                         set_cleanup,
                                         set_flushconsole,
                                         set_initoptions,
                                         set_readconsole,
                                         set_resetconsole,
                                         set_showfiles,
                                         set_showmessage,
                                         set_writeconsole_regular,
                                         set_writeconsole_warnerror,
                                         str_typeint,
                                         unserialize,
                                         BoolSexpVector,
                                         ByteSexpVector,
                                         ComplexSexpVector,
                                         CPLXSXP,
                                         CLOSXP,
                                         ENVSXP,
                                         EXPRSXP,
                                         EXTPTRSXP,
                                         FALSE,
                                         FloatSexpVector,
                                         IntSexpVector,
                                         INTSXP,
                                         ListSexpVector,
                                         LANGSXP,
                                         LISTSXP,
                                         LGLSXP,
                                         MissingArg,
                                         NACharacterType,
                                         NAComplexType,
                                         NAIntegerType,
                                         NALogicalType,
                                         NARealType,
                                         NA_Character,
                                         NA_Complex,
                                         NA_Logical,
                                         NA_Real,
                                         NULL,
                                         REALSXP,
                                         R_LEN_T_MAX,
                                         R_VERSION_BUILD,
                                         R_NilValue,
                                         RNULLType,
                                         RParsingError,
                                         RParsingIncompleteError,
                                         RRuntimeError,
                                         Sexp,
                                         SexpClosure,
                                         SexpEnvironment,
                                         SexpExtPtr,
                                         SexpSymbol,
                                         SexpS4,
                                         SexpVector,
                                         StrSexpVector,
                                         STRSXP,
                                         SYMSXP,
                                         TRUE,
                                         VECSXP)
from rpy2.rinterface import _rinterface


_REFERENCE_TO_R_SESSIONS = 'https://github.com/rstudio/reticulate/issues/98'

def get_r_session_status(r_session_init = None):
    """Return information about the R session, if available.

    Information about the R session being already initialized can be communicated by a parent environment.
    See discussion at: %s
    """ % _REFERENCE_TO_R_SESSIONS
    
    d = {'current_pid': os.getpid()}
    
    if r_session_init is None:
        r_session_init = os.environ.get('R_SESSION_INITIALIZED')
    if r_session_init:
        for item in r_session_init.split(':'):
            try:
                key, value = item.lsplit('=', 1)
            except ValueError:
                warnings.warn('The item %s in R_SESSION_INITIALIZED should be of the form key=value.' % item)
            d[key] = value
    return d


def is_r_externally_initialized():
    r_session_status = get_r_session_status()

    return r_session_status['current_pid'] == r_session_status.get('PID')


def set_python_session_status():
    """Set information about the Python process in an environment variable.

    Current the information See discussion at: %s
    """ % _REFERENCE_TO_R_SESSIONS
    
    d = collections.OrderedDict((('current_pid', os.getpid()),
                                ('sys.executable', sys.executable)))
    info_string = ':'.join('%s=%s' % x for x in d.items())
    os.environ['PYTHON_SESSION_INITIALIZED'] = info_string


## rename function imported from C-extension to wrap it.

_initr = initr
def initr(r_preservehash=False):
    """"Wrapper around `rpy2.rinterface._rinterface.initr()`.

    This wrapper is adding the following:

    - R is only initialized if `is_r_externally_initialized()` is not
    true when this function is called.

    - After R is initialized, :func:`rpy2.rinterface.endr` is registered
    to be called when Python exits.
    
    - The environment variable "PYTHON_SESSION_INFO" is set (See %s).
    """ % _REFERENCE_TO_R_SESSIONS

    # Force the internal initialization flag if there is an environment
    # variable that indicates that R was alreay initialized in the current
    # process.

    if is_r_externally_initialized():
        _rinterface._force_initialized()

    # As soon as R is initialized, set the environment variable
    # PYTHON_SESSION_INFO
    _initr(r_preservehash=r_preservehash)
    atexit.register(endr, 0)
    set_python_session_status()

    
    # TODO: the use of global does seem to be a too good pattern.
    global NA_Integer
    NA_Integer = NAIntegerType()

    
# wrapper in case someone changes sys.stdout:
def consolePrint(x):
    print(x)
    

set_writeconsole_regular(consolePrint)


def consoleWarn(x):
    warnings.warn(x, RRuntimeWarning)
set_writeconsole_warnerror(consoleWarn)


def consoleFlush():
    sys.stdout.flush()

set_flushconsole(consoleFlush)


def consoleRead(prompt):
    text = input(prompt)
    text += "\n"
    return text


set_readconsole(consoleRead)


def consoleMessage(x):
    sys.stdout.write(x)

set_showmessage(consoleMessage)


def chooseFile(prompt):
    res = raw_input(prompt)
    return res
set_choosefile(chooseFile)

def showFiles(wtitle, titlefiles, rdel, pager):
    sys.stdout.write(titlefiles)

    for wt in wtitle:
        sys.stdout.write(wt[0])
        f = open(wt[1])
        for row in f:
            sys.stdout.write(row)
        f.close()
    return 0
set_showfiles(showFiles)

def rternalize(function):
    """ Takes an arbitrary Python function and wrap it
    in such a way that it can be called from the R side. """
    assert callable(function) #FIXME: move the test down to C
    rpy_fun = SexpExtPtr(function, tag = python_type_tag)
    #rpy_type = ri.StrSexpVector(('.Python', ))
    #FIXME: this is a hack. Find a better way.
    template = parse('function(...) { .External(".Python", foo, ...) }')
    template[0][2][1][2] = rpy_fun
    return baseenv['eval'](template)
  
# def cleanUp(saveact, status, runlast):
#     return True

# setCleanUp(cleanUp)
