import random
import math
from pytest import approx
from mitxgraders.helpers.mitmath.mathfuncs import (
    cot, arccot,
    csc, arccsc,
    sec, arcsec,
    coth, arccoth,
    csch, arccsch,
    sech, arcsech,
    ARRAY_ONLY_FUNCTIONS)
from mitxgraders.helpers.mitmath.math_array import MathArray, random_math_array

def test_math_functions():
    """Test the math functions that we've implemented"""
    x = random.uniform(0, 1)
    assert cot(x) == approx(1/math.tan(x))
    assert sec(x) == approx(1/math.cos(x))
    assert csc(x) == approx(1/math.sin(x))
    assert sech(x) == approx(1/math.cosh(x))
    assert csch(x) == approx(1/math.sinh(x))
    assert coth(x) == approx(1/math.tanh(x))
    assert arcsec(sec(x)) == approx(x)
    assert arccsc(csc(x)) == approx(x)
    assert arccot(cot(x)) == approx(x)
    assert arcsech(sech(x)) == approx(x)
    assert arccsch(csch(x)) == approx(x)
    assert arccoth(coth(x)) == approx(x)

    x = random.uniform(-1, 0)
    assert cot(x) == approx(1/math.tan(x))
    assert sec(x) == approx(1/math.cos(x))
    assert csc(x) == approx(1/math.sin(x))
    assert sech(x) == approx(1/math.cosh(x))
    assert csch(x) == approx(1/math.sinh(x))
    assert coth(x) == approx(1/math.tanh(x))
    assert -arcsec(sec(x)) == approx(x)
    assert arccsc(csc(x)) == approx(x)
    assert arccot(cot(x)) == approx(x)
    assert -arcsech(sech(x)) == approx(x)
    assert arccsch(csch(x)) == approx(x)
    assert arccoth(coth(x)) == approx(x)

def test_array_functions_preserve_type():

    for name in ['trans', 'ctrans', 'adj']:
        func = ARRAY_ONLY_FUNCTIONS[name]
        result = func(random_math_array((3, 3)))
        assert isinstance(result, MathArray)
