from functools import reduce
import operator


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

    def __init__(self, data):
        self.data = data
        self.predicate = lambda z: True

    def _filter(self, *args, **kwargs):
        q1 = [self.__get_condition(name, val)
              for name, val in kwargs.items()] if kwargs is not None else []
        # q2 = [args] if args is not None else []

        folded_query = self.__fold_query(q1)
        self.update_predicate(operator.and_, folded_query)

        return self

    def _or(self, *args, **kwargs):
        q1 = [self.__get_condition(name, val)
              for name, val in kwargs.items()] if kwargs is not None else []
        # q2 = [args] if args is not None else []

        folded_query = self.__fold_query(q1)
        self.update_predicate(operator.or_, folded_query)

        return self

    def _not(self, *args, **kwargs):
        q1 = [self.__get_condition(name, val)
              for name, val in kwargs.items()] if kwargs is not None else []
        # q2 = [args] if args is not None else []

        folded_query = self.__fold_query(q1)
        self.update_predicate(operator.and_, lambda z: not folded_query(z))

        return self

    def update_predicate(self, op, query):
        self.predicate = lambda z, tmp=self.predicate: op(tmp(z), query(z))

    def __fold_query(self, query):
        return lambda z: reduce(lambda prev, cur: prev(z) and cur(z), query) if len(query) > 1 else query[0](z)

    def __get_condition(self, name, val):
        return self.__operation[name](val)

    def __next__(self):
        pass

    def foo(self):
        for x in self.data:
            if self.predicate(x):
                print(x)
        return self


# m = Magic(range(20))
# m._filter(__gt=7, __lt=13).foo()._filter(__gt=9).foo()
a = Magic(range(100))
a._filter(__gt=3)._filter(__lte=5)._or(__lt=20, __gt=13)._not(__eq=15)
a.foo()