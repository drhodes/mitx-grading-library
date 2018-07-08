from __future__ import division # necessary for one of the doctests
import numpy as np
from numbers import Number
from mitxgraders.baseclasses import StudentFacingError
from mitxgraders.helpers.mathfunc import robust_pow

class MathArrayError(StudentFacingError):
    """
    Thrown by MathArray when anticipated errors are made.
    """

def is_number_zero(value):
    """
    Tests whether a value is the scalar number 0.

    >>> map(is_number_zero, [0, 0.0, 0j])
    [True, True, True]
    >>> is_number_zero(np.matrix([0, 0, 0]))
    False
    """
    return isinstance(value, Number) and value == 0

def is_scalar_zero(value):
    return isinstance(value, MathArray) and value.ndim == 0 and value.item() == 0

def is_square(array):
    return array.ndim == 2 and array.shape[0] == array.shape[1]

class MathArray(np.ndarray):
    """
    A modification of numpy's ndarray class that behaves more like a mathematician would expect.

    Terminology:
    ============
        - vector, 1 dimensional, e.g., MathArray([1, 2, 3])
        - matrix, 2 dimensional, e.g., MathArray([[1, 2], [3, 4]])
        - tensor, 3+ dimensional, e.g., MathArray([ [[1]], [[2]] ])

    Zero-dimensional arrays, e.g., MathArray(5) are also supported but should
    not occur in practice.

        - scalar: Python number OR zero-dimensional array

    Differences from numpy.ndarray:
    ==============================
        - Multiplication:
            - scalar * array = scales elements of array;
            - array * scalar = scales elements of array;
            If shapes are correct:
            - vector * vector = number
            - matrix * vector = vector
            - vector * vector = vector
            - matrix * matrix = matrix
            Any multiplication involving tensors and arrays of dimension >1 is not supported.
        - powers are only allowed for square matrices and integer-like exponents.
        - supports multiplication with a universal identity irrespective of own shape
        - supports addition/subtraction with a universal identity if MathArray is square matrix.
        - throws MathArrayError instances when anticipated errors are made.
        Raised with student-friendly error messages.
    """

    def __new__(cls, input_array):
        """
        Creates a new MathArray Instance.

        Note: The ndarray constructor is very low-level and apparently not meant
        to be used, hence we need our own. This is a quirk of subclassing
        ndarray. See https://docs.scipy.org/doc/numpy/user/basics.subclassing.html
        for more info.
        """
        obj = np.asarray(input_array).view(cls)
        return obj

    @property
    def shape_name(self):
        names = {
            0: 'scalar',
            1: 'vector',
            2: 'matrix',
        }
        return names.get(self.ndim, 'tensor')

    @property
    def description(self):
        if self.ndim == 0:
            return self.shape_name
        elif self.ndim == 1:
            return '{self.shape_name} of length {self.shape[0]}'.format(self=self)
        elif self.ndim == 2:
            return ('{self.shape_name} of shape (rows: {self.shape[0]}, cols: '
                    '{self.shape[1]})').format(self=self)
        else:
            return '{self.shape_name} of shape {self.shape}'.format(self=self)

    def __add__(self, other):
        if is_number_zero(other) or is_scalar_zero(other):
            return self

        elif isinstance(other, Number):
            if self.ndim == 0:
                return super(MathArray, self).__add__(other)
            raise MathArrayError("Cannot add/subtract scalars to a {self.shape_name}."
                                 .format(self=self))

        elif isinstance(other, IdentityMultiple):
            if is_square(self):
                return self.__add__(other.as_matrix(self.shape[0]))
            elif self.ndim == 2:
                raise MathArrayError("Cannot add/subtract multiples of the identity "
                                     "to a non-square matrix.")
            else:
                raise MathArrayError("Cannot add/subtract multiples of the identity "
                    "to a {self.shape_name}".format(self=self))

        elif isinstance(other, MathArray):
            if self.shape == other.shape:
                return super(MathArray, self).__add__(other)

            msg = ("Cannot add/subtract a {self.description} with a {other.description}.").format(
                self=self, other=other)
            raise MathArrayError(msg)

        raise TypeError("Cannot add/subtract object of {type} to a {self.description}.".format(
            type=type(other), self=self))

    def __radd__(self, other):
        return self.__add__(other)

    def __sub__(self, other):
        return self.__add__(-1*other)

    def __rsub__(self, other):
        return (-self).__add__(other) # pylint: disable=invalid-unary-operand-type

    def __mul__(self, other):
        if isinstance(other, Number):
            return super(MathArray, self).__mul__(other)

        elif isinstance(other, IdentityMultiple):
            return super(MathArray, self).__mul__(other.value)

        elif isinstance(other, MathArray):
            if self.ndim == 0:
                return super(MathArray, other).__mul__(self.item())
            elif other.ndim == 0:
                return super(MathArray, self).__mul__(other.item())
            elif self.ndim > 2 or other.ndim > 2:
                raise MathArrayError("Multiplication of tensor arrays is not currently supported.")
            try:
                return np.dot(self, other)
            except ValueError:
                # vector-specific message mentions dot product
                if self.ndim == 1 and other.ndim == 1:
                    msg = ("Cannot calculate the dot product of a {self.description} "
                           "with a {other.description}".format(self=self, other=other))
                    raise MathArrayError(msg)
                # general message:
                msg = ("Cannot multiply a {self.description} with a {other.description}.").format(
                    self=self, other=other)
                raise MathArrayError(msg)

        raise TypeError("Cannot multiply object of {type} with a {self.description}.".format(
            type=type(other), self=self))

    def __rmul__(self, other):
        if isinstance(other, IdentityMultiple):
            other = other.value
        return super(MathArray, self).__rmul__(other)

    def __pow__(self, other):
        """
        Matrix powers for MathArrays of dimension 0 and 2.
        """
        if self.ndim == 0:
            if isinstance(other, Number):
                return robust_pow(self.item(), other)
            elif isinstance(other, MathArray):
                return other.__rpow__(self.item())
            else:
                raise TypeError("Cannot raise a scalar to a {type} power".format(type=type(other)))

        elif not self.ndim == 2:
            raise MathArrayError("Cannot raise a {self.shape_name} to powers.".format(
                self=self))

        elif not is_square(self):
            raise MathArrayError("Cannot raise a non-square matrix to powers.")

        # Henceforth, self is a square matrix:
        elif isinstance(other, int):
            return np.linalg.matrix_power(self, other)

        elif isinstance(other, float) and other.is_integer():
            return np.linalg.matrix_power(self, int(other))

        elif isinstance(other, Number):
            raise MathArrayError("Cannot raise a matrix to non-integer powers.")

        elif isinstance(other, MathArray):
            raise MathArrayError("Cannot raise a matrix to {other.shape_name} powers.".format(
                other=other))

        raise TypeError("Cannot raise matrix to power of type {type}.".format(
            type=type(other)))

    def __rpow__(self, other):
        if self.ndim == 0 and isinstance(other, Number):
            return robust_pow(other, self.item())

        if isinstance(other, Number):
            raise MathArrayError("Cannot raise a scalar to power of a {self.shape_name}."
                                 .format(self=self))
        raise TypeError("Cannot raise {type} to power of {self.shape_name}."
                            .format(type=type(other), self=self))

    def __rtruediv__(self, other):
        if isinstance(self, MathArray) and self.ndim >0:
            raise MathArrayError("Cannot divide by a {self.shape_name}".format(self=self))
        return super(MathArray, self).__rtruediv__(other)


def equal_as_arrays(A, B):
    math_arrays = isinstance(A, MathArray) and isinstance(B, MathArray)
    values_equal = np.array_equal(A, B)
    return math_arrays and values_equal and A.shape == B.shape


class IdentityMultiple(object):
    """
    Represents a multiple of the identity matrix.

    Instantiation:
    ==============

    Instantiate with a single value:
    >>> IdentityMultiple(5)
    5*Identity

    If instantiated with 0, the number 0 is returned:
    >>> IdentityMultiple(0) == 0
    True

    Comparisons:
    ============
    >>> IdentityMultiple(5) == IdentityMultiple(5)
    True
    >>> IdentityMultiple(5) == IdentityMultiple(3)
    False
    >>> IdentityMultiple(5) == 5
    False

    Unary Operations:
    =================
    They work:
    >>> +IdentityMultiple(5)
    5*Identity
    >>> -IdentityMultiple(5)
    -5*Identity

    Binary Operations:
    ==================
    When IdentityMultiple is involved in any binary operation, it delegates
    calculation to the other operand except in a few special cases, illustrated
    below.

    >>> import random
    >>> a, b = random.uniform(-10, 10), random.uniform(-10, 10)
    >>> I = IdentityMultiple

    Addition with zero:
    >>> assert I(a) + 0 == 0 + I(a) == I(a)

    Subtraction with zero:
    >>> assert I(a) - 0 == I(a)
    >>> assert 0 - I(a) == -I(a)

    Multiplication with scalars:
    >>> assert b*I(a) == I(a)*b == I(a*b)

    Division with scalars:
    >>> assert I(a)/b == I(a/b)
    >>> b/I(a)
    Traceback (most recent call last):
    TypeError: unsupported operand type(s) for /: 'float' and 'IdentityMultiple'

    Scalar powers:
    >>> c = random.uniform(1, 10) # make sure the base is positive
    >>> assert I(c)**a == I(c**a)

    Addition, Subtraction, and Multiplication with other IdentityMultiples:
    >>> assert I(a) + I(b) == I(a + b)
    >>> assert I(a) - I(b) == I(a - b)
    >>> assert I(a) * I(b) == I(a*b)

    Since I(0)==0, sums and differences might be scalar 0:
    >>> assert I(a) - I(a) == 0
    """
    def __new__(cls, value):
        if is_number_zero(value):
            return 0
        return super(IdentityMultiple, cls).__new__(cls, value)

    def as_matrix(self, n):
        """
        Returns a multiple of the n by n identity matrix.

        >>> S = IdentityMultiple(4)
        >>> S_mat2 = S.as_matrix(2)
        >>> S_mat2.tolist()
        [[4.0, 0.0], [0.0, 4.0]]
        >>> isinstance(S_mat2, MathArray)
        True
        """
        elements = (self.value*np.identity(n))
        return MathArray(elements)

    def __init__(self, value):
        self.value = value

    def __repr__(self):
        return "{value}*Identity".format(value=self.value)

    def __eq__(self, other):
        if isinstance(other, IdentityMultiple):
            return self.value == other.value
        return False

    def __pos__(self):
        return self
    def __neg__(self):
        return IdentityMultiple(-self.value)

    def __add__(self, other):
        if is_number_zero(other):
            return self
        elif isinstance(other, IdentityMultiple):
            return IdentityMultiple(self.value + other.value)
        return other.__radd__(self)

    def __radd__(self, other):
        return self.__add__(other)

    def __sub__(self, other):
        if is_number_zero(other):
            return self
        elif isinstance(other, IdentityMultiple):
            return IdentityMultiple(self.value - other.value)
        return other.__rsub__(self)

    def __rsub__(self, other):
        return (-self).__add__(other)

    def __mul__(self, other):
        if isinstance(other, Number):
            return IdentityMultiple(self.value*other)
        elif isinstance(other, IdentityMultiple):
            return IdentityMultiple(self.value*other.value)
        return other.__rmul__(self)

    def __rmul__(self, other):
        return self.__mul__(other)

    def __truediv__(self, other):
        if isinstance(other, Number):
            return IdentityMultiple(self.value/other)
        return other.__rtruediv__(self)

    def __pow__(self, other):
        if isinstance(other, Number):
            return IdentityMultiple(self.value**other)
        return other.__rpow__(self)
