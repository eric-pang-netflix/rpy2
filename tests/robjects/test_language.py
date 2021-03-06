import pytest
import rpy2.robjects as robjects
import rpy2.robjects.language as lg
rinterface = robjects.rinterface


@pytest.fixture(scope='module')
def clean_globalenv():
    for name in ('x', 'y'):
        del robjects.globalenv[name]


def test_eval():
    code = """
    x <- 1+2
    y <- (x+1) / 2
    """
    res = lg.eval(code)
    assert 'x' in robjects.globalenv.keys()
    assert robjects.globalenv['x'][0] == 3
    assert 'y' in robjects.globalenv.keys()
    assert robjects.globalenv['y'][0] == 2

    
def testeval_in_environment():
    code = """
    x <- 1+2
    y <- (x+1) / 2
    """
    env = robjects.Environment()
    res = lg.eval(code, envir=env)
    assert 'x' in env.keys()
    assert env['x'][0] == 3
    assert 'y' in env.keys()
    assert env['y'][0] == 2

