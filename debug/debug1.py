# -*- coding: utf-8 -*-
"""
Created on Tue Jun 22 16:30:10 2021

@author: Julien Panteri
"""
from typing import overload, Union
from typing_extensions import Literal


@overload
def test_func(arg1: int, kwarg1: int = 0, ret_str: Literal[True] = ...) -> str: ...

@overload
def test_func(arg1: int, kwarg1: int, ret_str: Literal[False]) -> int: ...

@overload
def test_func(arg1: int, kwarg1: int = 0, *, ret_str: Literal[False]) -> int: ...


def test_func(arg1: int, kwarg1: int = 0, ret_str: bool = True) -> Union[int, str]:
    return "Hello " if ret_str else 0


if __name__ == "__main__":
    print(test_func(0) + "World!")
    print(test_func(0, 0) + "World!")
    print(test_func(0, 0, True) + "World!")
    print(test_func(0, 0, False) + 10)
    print(test_func(0, ret_str=False) + 1)
    print(test_func(0, 0, ret_str=False) + 1)
    print(test_func(0, ret_str=True) + "World!")
    print(test_func(0, 0, ret_str=True) + "World!")