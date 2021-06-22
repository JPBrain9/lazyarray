# -*- coding: utf-8 -*-
"""
Created on Tue Jun 22 16:46:52 2021

@author: Julien Panteri
"""
import numbers
import operator
from copy import deepcopy
import collections
from functools import wraps, reduce
import logging
from typing import Callable, Union,Tuple, overload, Literal
from collections.abc import Sequence

#https://stackoverflow.com/questions/6434482/python-function-overloading

import numpy as np
try:
    from scipy import sparse
    from scipy.sparse import bsr_matrix, coo_matrix, csc_matrix, csr_matrix, dia_matrix, dok_matrix, lil_matrix
    have_scipy = True
except ImportError:
    have_scipy = False
def is_array_like(value : Union[int,float,bool,np.ndarray, Callable]): 
    # False for numbers, generators, functions, iterators
    if not isinstance(value, collections.Sized):
        return False
    if sparse.issparse(value):
        return True
    if isinstance(value, collections.Mapping):
        # because we may wish to have lazy arrays in which each
        # item is a dict, for example
        return False
    if getattr(value, "is_lazyarray_scalar", False):
        # for user-defined classes that are "Sized" but that should
        # be treated as individual elements in a lazy array
        # the attribute "is_lazyarray_scalar" can be defined with value
        # True.
        return False
    return True



class larray(object):
    """
    Optimises storage of and operations on arrays in various ways:
      - stores only a single value if all the values in the array are the same;
      - if the array is created from a function `f(i)` or `f(i,j)`, then
        elements are only evaluated when they are accessed. Any operations
        performed on the array are also queued up to be executed on access.
    Two use cases for the latter are:
      - to save memory for very large arrays by accessing them one row or
        column at a time: the entire array need never be in memory.
      - in parallelized code, different rows or columns may be evaluated
        on different nodes or in different threads.
    """


    def __init__(self, value : Union[int,float,bool,np.ndarray, Callable], shape=None, dtype=None):
        """
        Create a new lazy array.
        `value` : may be an int, float, bool, NumPy array, iterator,
                  generator or a function, `f(i)` or `f(i,j)`, depending on the
                  dimensions of the array.
        `f(i,j)` should return a single number when `i` and `j` are integers,
        and a 1D array when either `i` or `j` or both is a NumPy array (in the
        latter case the two arrays must have equal lengths).
        """

        self.dtype = dtype
        self.operations = []
        if isinstance(value, str):
            raise TypeError("An larray cannot be created from a string")
        elif isinstance(value, larray):
            if shape is not None and value.shape is not None:
                assert shape == value.shape
            self._shape = shape or value.shape
            self.base_value = value.base_value
            self.dtype = dtype or value.dtype
            self.operations = value.operations  # should deepcopy?

        elif is_array_like(value):  # False for numbers, generators, functions, iterators
            if have_scipy and sparse.issparse(value):  # For sparse matrices
                self.dtype = dtype or value.dtype
            elif not isinstance(value, np.ndarray):
                value = np.array(value, dtype=dtype)
            elif dtype is not None:
               assert np.can_cast(value.dtype, dtype, casting='safe')  # or could convert value to the provided dtype
            if shape and value.shape and value.shape != shape:
                raise ValueError("Array has shape %s, value has shape %s" % (shape, value.shape))
            if value.shape:
                self._shape = value.shape
            else:
                self._shape = shape
            self.base_value = value

        else:
            assert np.isreal(value)  # also True for callables, generators, iterators
            self._shape = shape
            if dtype is None or isinstance(value, dtype):
                self.base_value = value
            else:
                try:
                    self.base_value = dtype(value)
                except TypeError:
                    self.base_value = value