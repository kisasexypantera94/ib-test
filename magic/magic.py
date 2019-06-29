from __future__ import annotations

import operator
from functools import reduce
from typing import *


class Magic:
    __relations = {
        "eq": lambda y: lambda x: x == y,
        "lt": lambda y: lambda x: x < y,
        "lte": lambda y: lambda x: x <= y,
        "gte": lambda y: lambda x: x >= y,
        "gt": lambda y: lambda x: x > y,
        "ne": lambda y: lambda x: x != y,
        "in": lambda y: lambda x: x in y,
        "startswith": lambda y: lambda x: x.startswith(y)
    }

    def __init__(self: Magic, data: Iterable, predicate: Callable[bool] = lambda z: True) -> None:
        self.data = data
        self.predicate = predicate

    def __iter__(self: Magic):
        for x in self.data:
            try:
                if self.predicate(x):
                    yield x
            except TypeError:
                pass

    def filter_(self: Magic, *args: Magic, **kwargs: object) -> Magic:
        predicate_from_query = self.__process_query(args, kwargs)
        return self.__new_magic(operator.and_, predicate_from_query)

    def or_(self: Magic, *args: Magic, **kwargs: object) -> Magic:
        predicate_from_query = self.__process_query(args, kwargs)
        return self.__new_magic(operator.or_, predicate_from_query)

    def not_(self: Magic, *args: Magic, **kwargs: object) -> Magic:
        predicate_from_query = self.__process_query(args, kwargs)
        return self.__new_magic(operator.and_, lambda z: not predicate_from_query(z))

    def __process_query(self: Magic, predicates: Tuple[Magic], conditions: Dict[str, object]) -> Callable[bool]:
        query = self.__parse_query(conditions) + [m.predicate for m in predicates]
        folded_query = self.__fold_query(query)
        return folded_query

    def __parse_query(self: Magic, query: Dict[str, object]) -> List[Callable[bool]]:
        return [self.__make_function(name, val) for name, val in query.items()]

    def __make_function(self: Magic, name: str, val: object) -> Callable[bool]:
        """Парсинг условия и преобразование его в функцию"""
        attributes = name.split("__")
        relation_with_val = self.__get_relation(attributes[-1], val)

        def foo(obj: object) -> bool:
            cur = obj
            for attr in attributes[:-1]:
                if not attr:
                    break

                if hasattr(cur, attr):
                    cur = getattr(cur, attr)
                else:
                    return False

            return relation_with_val(cur)

        return foo

    def __get_relation(self: Magic, name: str, val: object) -> Callable[bool]:
        return self.__relations[name](val)

    @staticmethod
    def __fold_query(query: List[Callable[bool]]) -> Callable[bool]:
        """Логическое перемножение булевых функций"""
        return lambda z: reduce(lambda prev, cur: prev(z) and cur(z), query) if len(query) > 1 else query[0](z)

    def __new_magic(self: Magic, op: Callable[bool], new: Callable[bool]) -> Magic:
        """Создание обновленного объекта `Magic`"""
        new_predicate = lambda z, old=self.predicate: op(old(z), new(z))
        return Magic(self.data, new_predicate)
