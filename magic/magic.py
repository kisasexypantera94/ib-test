from __future__ import annotations

import operator
from functools import reduce
from typing import *


class Magic:
    __operation = {
        "__eq": lambda y: lambda x: x == y,
        "__lt": lambda y: lambda x: x < y,
        "__lte": lambda y: lambda x: x <= y,
        "__gte": lambda y: lambda x: x >= y,
        "__gt": lambda y: lambda x: x > y,
        "__ne": lambda y: lambda x: x != y,
        "__in": lambda y: lambda x: x in y,
    }

    def __init__(self: Magic, data: Iterable) -> None:
        self.data = data
        self.predicate = lambda z: True

    def __iter__(self: Magic):
        for x in self.data:
            if self.predicate(x):
                yield x

    def filter_(self: Magic, *args: Magic, **kwargs: object) -> Magic:
        query = self.__parse_query(kwargs)
        folded_query = self.__fold_query(query)
        self.__update_predicate(operator.and_, folded_query)

        return self

    def or_(self: Magic, *args: Magic, **kwargs: object) -> Magic:
        query = self.__parse_query(kwargs)
        folded_query = self.__fold_query(query)
        self.__update_predicate(operator.or_, folded_query)

        return self

    def not_(self: Magic, *args: Magic, **kwargs: object) -> Magic:
        query = self.__parse_query(kwargs)
        folded_query = self.__fold_query(query)
        self.__update_predicate(operator.and_, lambda z: not folded_query(z))

        return self

    def __update_predicate(self: Magic, op: Callable, new: Callable) -> None:
        self.predicate = lambda z, old=self.predicate: op(old(z), new(z))

    def __parse_query(self: Magic, query: dict) -> list:
        return [self.__get_condition(name, val) for name, val in query.items()] if query is not None else []

    @staticmethod
    def __fold_query(query: list) -> Callable:
        return lambda z: reduce(lambda prev, cur: prev(z) and cur(z), query) if len(query) > 1 else query[0](z)

    def __get_condition(self: Magic, name: str, val: object) -> Callable:
        return self.__operation[name](val)
